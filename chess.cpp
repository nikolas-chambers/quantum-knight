// Teacher's engine (0x88). Full legal movegen, perft, UCI, alpha-beta search.
#include <bits/stdc++.h>
#include <cstdint>
using namespace std;
typedef uint64_t u64;

// pieces: 0 empty; sign = color. Use chars: PNBRQK / pnbrqk
enum { EMPTY=0 };
int board[128];
int sideToMove;            // 0 white, 1 black
int castling;              // bits: 1=K 2=Q 4=k 8=q
int epSquare;              // 0x88 square or -1
int kingSq[2];

inline bool onBoard(int s){ return !(s & 0x88); }
inline int fileOf(int s){ return s & 7; }
inline int rankOf(int s){ return s >> 4; }
inline int sq(int f,int r){ return r*16+f; }

int colorOf(int p){ // 0 white,1 black, -1 empty
  if(p==EMPTY) return -1;
  return (p=='P'||p=='N'||p=='B'||p=='R'||p=='Q'||p=='K')?0:1;
}
int typeOf(int p){ int c=tolower(p); return c; } // 'p','n','b','r','q','k'

const int KN[8]={33,31,18,14,-33,-31,-18,-14};
const int KG[8]={16,-16,1,-1,17,15,-17,-15};
const int BD[4]={17,15,-17,-15};
const int RD[4]={16,-16,1,-1};

bool squareAttacked(int s,int by){ // is s attacked by color 'by'
  // pawns
  if(by==0){ if(onBoard(s-17)&&board[s-17]=='P')return true; if(onBoard(s-15)&&board[s-15]=='P')return true; }
  else { if(onBoard(s+17)&&board[s+17]=='p')return true; if(onBoard(s+15)&&board[s+15]=='p')return true; }
  // knights
  for(int d:KN){ int t=s+d; if(onBoard(t)){ int p=board[t]; if(p&&colorOf(p)==by&&typeOf(p)=='n')return true; } }
  // king
  for(int d:KG){ int t=s+d; if(onBoard(t)){ int p=board[t]; if(p&&colorOf(p)==by&&typeOf(p)=='k')return true; } }
  // bishop/queen diagonals
  for(int d:BD){ int t=s+d; while(onBoard(t)){ int p=board[t]; if(p){ if(colorOf(p)==by&&(typeOf(p)=='b'||typeOf(p)=='q'))return true; break;} t+=d; } }
  // rook/queen lines
  for(int d:RD){ int t=s+d; while(onBoard(t)){ int p=board[t]; if(p){ if(colorOf(p)==by&&(typeOf(p)=='r'||typeOf(p)=='q'))return true; break;} t+=d; } }
  return false;
}

struct Move{ int from,to,promo,flag; }; // flag:0 normal,1 doublepush,2 ep,3 castleK,4 castleQ
struct Undo{ int captured,castling,epSquare,kingW,kingB; int capSq; };

void genMoves(vector<Move>&mv){
  int us=sideToMove, them=us^1;
  for(int s=0;s<128;s++){ if(!onBoard(s))continue; int p=board[s]; if(!p||colorOf(p)!=us)continue;
    int t=typeOf(p);
    if(t=='p'){
      int fwd = us==0?16:-16; int startRank=us==0?1:6; int promoRank=us==0?6:1;
      int one=s+fwd;
      if(onBoard(one)&&board[one]==EMPTY){
        if(rankOf(s)==promoRank){ for(int pr: {'q','r','b','n'}) mv.push_back({s,one,pr,0}); }
        else { mv.push_back({s,one,0,0});
          int two=s+2*fwd; if(rankOf(s)==startRank&&board[two]==EMPTY) mv.push_back({s,two,0,1}); }
      }
      for(int cd: {fwd+1,fwd-1}){ int c=s+cd; if(!onBoard(c))continue;
        if(board[c]&&colorOf(board[c])==them){
          if(rankOf(s)==promoRank){ for(int pr:{'q','r','b','n'}) mv.push_back({s,c,pr,0}); }
          else mv.push_back({s,c,0,0});
        } else if(c==epSquare && epSquare!=-1){ mv.push_back({s,c,0,2}); }
      }
    } else if(t=='n'){ for(int d:KN){ int c=s+d; if(onBoard(c)&&(board[c]==EMPTY||colorOf(board[c])==them)) mv.push_back({s,c,0,0}); } }
    else if(t=='k'){ for(int d:KG){ int c=s+d; if(onBoard(c)&&(board[c]==EMPTY||colorOf(board[c])==them)) mv.push_back({s,c,0,0}); }
      // castling
      if(us==0){
        if((castling&1)&&board[sq(5,0)]==EMPTY&&board[sq(6,0)]==EMPTY&&board[sq(7,0)]=='R'
           &&!squareAttacked(sq(4,0),1)&&!squareAttacked(sq(5,0),1)&&!squareAttacked(sq(6,0),1)) mv.push_back({s,sq(6,0),0,3});
        if((castling&2)&&board[sq(3,0)]==EMPTY&&board[sq(2,0)]==EMPTY&&board[sq(1,0)]==EMPTY&&board[sq(0,0)]=='R'
           &&!squareAttacked(sq(4,0),1)&&!squareAttacked(sq(3,0),1)&&!squareAttacked(sq(2,0),1)) mv.push_back({s,sq(2,0),0,4});
      } else {
        if((castling&4)&&board[sq(5,7)]==EMPTY&&board[sq(6,7)]==EMPTY&&board[sq(7,7)]=='r'
           &&!squareAttacked(sq(4,7),0)&&!squareAttacked(sq(5,7),0)&&!squareAttacked(sq(6,7),0)) mv.push_back({s,sq(6,7),0,3});
        if((castling&8)&&board[sq(3,7)]==EMPTY&&board[sq(2,7)]==EMPTY&&board[sq(1,7)]==EMPTY&&board[sq(0,7)]=='r'
           &&!squareAttacked(sq(4,7),0)&&!squareAttacked(sq(3,7),0)&&!squareAttacked(sq(2,7),0)) mv.push_back({s,sq(2,7),0,4});
      }
    } else { const int*dir; int n; if(t=='b'){dir=BD;n=4;} else if(t=='r'){dir=RD;n=4;} else {dir=KG;n=8;}
      for(int i=0;i<n;i++){ int c=s+dir[i]; while(onBoard(c)){ if(board[c]==EMPTY) mv.push_back({s,c,0,0});
        else { if(colorOf(board[c])==them) mv.push_back({s,c,0,0}); break; } c+=dir[i]; } }
    }
  }
}

void makeMove(const Move&m,Undo&u){
  int us=sideToMove, them=us^1;
  u.castling=castling; u.epSquare=epSquare; u.kingW=kingSq[0]; u.kingB=kingSq[1];
  u.captured=EMPTY; u.capSq=-1;
  int piece=board[m.from];
  // ep capture
  if(m.flag==2){ int capPawnSq = m.to + (us==0?-16:16); u.captured=board[capPawnSq]; u.capSq=capPawnSq; board[capPawnSq]=EMPTY; }
  else if(board[m.to]!=EMPTY){ u.captured=board[m.to]; u.capSq=m.to; }
  board[m.to]=piece; board[m.from]=EMPTY;
  if(m.promo) board[m.to]= us==0?toupper(m.promo):tolower(m.promo);
  if(typeOf(piece)=='k') kingSq[us]=m.to;
  // castling rook move
  if(m.flag==3){ if(us==0){ board[sq(5,0)]=board[sq(7,0)]; board[sq(7,0)]=EMPTY;} else { board[sq(5,7)]=board[sq(7,7)]; board[sq(7,7)]=EMPTY;} }
  if(m.flag==4){ if(us==0){ board[sq(3,0)]=board[sq(0,0)]; board[sq(0,0)]=EMPTY;} else { board[sq(3,7)]=board[sq(0,7)]; board[sq(0,7)]=EMPTY;} }
  // update castling rights
  if(piece=='K') castling&=~3; if(piece=='k') castling&=~12;
  if(m.from==sq(7,0)||m.to==sq(7,0)) castling&=~1;
  if(m.from==sq(0,0)||m.to==sq(0,0)) castling&=~2;
  if(m.from==sq(7,7)||m.to==sq(7,7)) castling&=~4;
  if(m.from==sq(0,7)||m.to==sq(0,7)) castling&=~8;
  // ep square
  epSquare=-1; if(m.flag==1) epSquare = m.from + (us==0?16:-16);
  sideToMove=them;
}
void unmakeMove(const Move&m,const Undo&u){
  int them=sideToMove, us=them^1;
  sideToMove=us; castling=u.castling; epSquare=u.epSquare; kingSq[0]=u.kingW; kingSq[1]=u.kingB;
  int piece=board[m.to];
  if(m.promo) piece = us==0?'P':'p';
  board[m.from]=piece; board[m.to]=EMPTY;
  if(m.flag==3){ if(us==0){ board[sq(7,0)]=board[sq(5,0)]; board[sq(5,0)]=EMPTY;} else { board[sq(7,7)]=board[sq(5,7)]; board[sq(5,7)]=EMPTY;} }
  if(m.flag==4){ if(us==0){ board[sq(0,0)]=board[sq(3,0)]; board[sq(3,0)]=EMPTY;} else { board[sq(0,7)]=board[sq(3,7)]; board[sq(3,7)]=EMPTY;} }
  if(u.capSq!=-1) board[u.capSq]=u.captured;
}

bool inCheck(int us){ return squareAttacked(kingSq[us], us^1); }

void legalMoves(vector<Move>&out){
  vector<Move> ps; genMoves(ps); int us=sideToMove;
  for(auto&m:ps){ Undo u; makeMove(m,u); if(!squareAttacked(kingSq[us], us^1)) out.push_back(m); unmakeMove(m,u); }
}

u64 perft(int depth){
  if(depth==0) return 1;
  vector<Move> mv; legalMoves(mv); if(depth==1) return mv.size();
  u64 n=0; for(auto&m:mv){ Undo u; makeMove(m,u); n+=perft(depth-1); unmakeMove(m,u);} return n;
}

void setFen(const string&fen){
  for(int i=0;i<128;i++) board[i]=EMPTY;
  istringstream is(fen); string b,stm,cr,ep; is>>b>>stm>>cr>>ep;
  int r=7,f=0; for(char c:b){ if(c=='/'){r--;f=0;} else if(isdigit(c)) f+=c-'0'; else { board[sq(f,r)]=c; f++; } }
  sideToMove = stm=="w"?0:1;
  castling=0; for(char c:cr){ if(c=='K')castling|=1; if(c=='Q')castling|=2; if(c=='k')castling|=4; if(c=='q')castling|=8; }
  epSquare=-1; if(ep!="-"&&ep.size()==2) epSquare=sq(ep[0]-'a', ep[1]-'1');
  for(int s=0;s<128;s++) if(onBoard(s)){ if(board[s]=='K')kingSq[0]=s; if(board[s]=='k')kingSq[1]=s; }
}

// ---- eval + search ----
int val[256]; // by piece char
void initVal(){ val['P']=100;val['N']=320;val['B']=330;val['R']=500;val['Q']=900;val['K']=20000;
  val['p']=-100;val['n']=-320;val['b']=-330;val['r']=-500;val['q']=-900;val['k']=-20000; }
const int PST_P[64]={0,0,0,0,0,0,0,0, 5,10,10,-20,-20,10,10,5, 5,-5,-10,0,0,-10,-5,5, 0,0,0,20,20,0,0,0, 5,5,10,25,25,10,5,5, 10,10,20,30,30,20,10,10, 50,50,50,50,50,50,50,50, 0,0,0,0,0,0,0,0};
const int PST_N[64]={-50,-40,-30,-30,-30,-30,-40,-50, -40,-20,0,0,0,0,-20,-40, -30,0,10,15,15,10,0,-30, -30,5,15,20,20,15,5,-30, -30,0,15,20,20,15,0,-30, -30,5,10,15,15,10,5,-30, -40,-20,0,5,5,0,-20,-40, -50,-40,-30,-30,-30,-30,-40,-50};
const int PST_B[64]={-20,-10,-10,-10,-10,-10,-10,-20, -10,5,0,0,0,0,5,-10, -10,10,10,10,10,10,10,-10, -10,0,10,10,10,10,0,-10, -10,5,5,10,10,5,5,-10, -10,0,5,10,10,5,0,-10, -10,0,0,0,0,0,0,-10, -20,-10,-10,-10,-10,-10,-10,-20};
const int PST_K[64]={20,30,10,0,0,10,30,20, 20,20,0,0,0,0,20,20, -10,-20,-20,-20,-20,-20,-20,-10, -20,-30,-30,-40,-40,-30,-30,-20, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30};
int evaluate() {
  int s = 0;
  for (int q = 0; q < 128; q++) {
    if (!onBoard(q) || !board[q]) continue;
    int p = board[q];
    s += val[p];
    int mi = (colorOf(p) == 0) ? (rankOf(q) * 8 + fileOf(q)) : ((rankOf(q) * 8 + fileOf(q)) ^ 56);
    int t = typeOf(p), ps = 0;
    if (t == 'p') ps = PST_P[mi]; 
    else if (t == 'n') ps = PST_N[mi]; 
    else if (t == 'b') ps = PST_B[mi]; 
    else if (t == 'k') ps = PST_K[mi];
    s += (colorOf(p) == 0) ? ps : -ps;
  }

  // Passed pawns
  for (int q = 0; q < 128; q++) {
    if (!onBoard(q) || board[q] != 'p' && board[q] != 'P') continue;
    int p = board[q];
    int rank = rankOf(q);
    int file = fileOf(q);
    bool passed = true;
    for (int r = (colorOf(p) == 0) ? rank + 1 : rank - 1; (colorOf(p) == 0) ? r < 8 : r >= 0; r += (colorOf(p) == 0) ? 1 : -1) {
      if (board[(r * 8) + file] == (colorOf(p) == 0) ? 'p' : 'P') {
        passed = false;
        break;
      }
    }
    if (passed) s += (colorOf(p) == 0) ? 50 : -50;
  }

  // Rook on open or half-open file
  for (int q = 0; q < 128; q++) {
    if (!onBoard(q) || board[q] != 'r' && board[q] != 'R') continue;
    int p = board[q];
    int file = fileOf(q);
    bool open = true;
    bool halfOpen = false;
    for (int r = 0; r < 8; r++) {
      if (board[(r * 8) + file] == (colorOf(p) == 0) ? 'p' : 'P') {
        open = false;
        halfOpen = true;
      }
    }
    if (open) s += (colorOf(p) == 0) ? 20 : -20;
    else if (halfOpen) s += (colorOf(p) == 0) ? 10 : -10;
  }

  // King pawn shield
  for (int q = 0; q < 128; q++) {
    if (!onBoard(q) || board[q] != 'p' && board[q] != 'P') continue;
    int p = board[q];
    int rank = rankOf(q);
    int file = fileOf(q);
    if ((colorOf(p) == 0 && rank >= 6) || (colorOf(p) == 1 && rank <= 1)) {
      if (fileOf(kingSq[colorOf(p)]) == file || fileOf(kingSq[colorOf(p)]) == file + 1 || fileOf(kingSq[colorOf(p)]) == file - 1) {
        s += (colorOf(p) == 0) ? 10 : -10;
      }
    }
  }

  // Bishop pair
  int whiteBishops = 0;
  int blackBishops = 0;
  for (int q = 0; q < 128; q++) {
    if (!onBoard(q) || board[q] != 'b' && board[q] != 'B') continue;
    if (colorOf(board[q]) == 0) whiteBishops++;
    else blackBishops++;
  }
  if (whiteBishops >= 2) s += 50;
  if (blackBishops >= 2) s -= 50;

  return sideToMove == 0 ? s : -s;
}

string sqName(int s){ string r; r+=('a'+fileOf(s)); r+=('1'+rankOf(s)); return r; }
string moveStr(const Move&m){ string r=sqName(m.from)+sqName(m.to); if(m.promo) r+=char(tolower(m.promo)); return r; }

long long nodes;

// ---- Zobrist hashing ----
u64 zPiece[256][128], zSide;
void initZobrist(){ std::mt19937_64 rng(0x9E3779B97F4A7C15ULL);
  for(int p=0;p<256;p++) for(int s=0;s<128;s++) zPiece[p][s]=rng();
  zSide=rng(); }
u64 hashPos(){ u64 h=0;
  for(int s=0;s<128;s++){ if(onBoard(s)&&board[s]) h^=zPiece[board[s]][s]; }
  if(sideToMove) h^=zSide; return h; }

// ---- Transposition table ----
enum{ TT_EXACT=0, TT_LOWER=1, TT_UPPER=2 };
struct TTE{ u64 key; int depth; int score; int flag; Move best; };
const int TT_BITS=22, TT_SIZE=1<<TT_BITS, TT_MASK=TT_SIZE-1;
vector<TTE> TT(TT_SIZE);
void ttClear(){ for(auto&e:TT){ e.key=0; e.depth=-1; } }

// ---- move ordering ----
Move killers[128][2];
inline int mvvlva(const Move&m){            // victim high, attacker low
  int vic=board[m.to], att=board[m.from];
  int vv = vic?abs(val[vic]):(m.flag==2?100:0);   // en-passant captures a pawn
  return vv*16 - (att?abs(val[att]):0); }
void orderMoves(vector<Move>&mv,const Move&ttm,int ply){
  vector<pair<int,Move>> sc; sc.reserve(mv.size());
  for(auto&m:mv){ int s;
    bool cap = board[m.to]!=EMPTY || m.flag==2;
    if(ttm.from!=ttm.to && m.from==ttm.from && m.to==ttm.to && m.promo==ttm.promo) s=1000000;
    else if(cap) s=100000+mvvlva(m);
    else if((killers[ply][0].from==m.from&&killers[ply][0].to==m.to)) s=90000;
    else if((killers[ply][1].from==m.from&&killers[ply][1].to==m.to)) s=80000;
    else s=0;
    sc.push_back({s,m}); }
  sort(sc.begin(),sc.end(),[](const pair<int,Move>&a,const pair<int,Move>&b){ return a.first>b.first; });
  for(size_t i=0;i<mv.size();i++) mv[i]=sc[i].second;
}

int qsearch(int alpha,int beta){
  int stand=evaluate(); if(stand>=beta) return beta; if(stand>alpha) alpha=stand;
  vector<Move> mv; legalMoves(mv);
  Move none{0,0,0,0}; orderMoves(mv,none,0);
  for(auto&m:mv){ if(board[m.to]==EMPTY && m.flag!=2) continue;   // captures only (incl. en passant)
    Undo u; makeMove(m,u); nodes++; int sc=-qsearch(-beta,-alpha); unmakeMove(m,u);
    if(sc>=beta) return beta; if(sc>alpha) alpha=sc; }
  return alpha;
}
int negamax(int depth,int alpha,int beta,int ply){
  if(depth==0){ return qsearch(alpha,beta); }
  u64 key=hashPos(); TTE&e=TT[key&TT_MASK];
  Move ttm{0,0,0,0}; int alphaOrig=alpha;
  if(e.key==key && e.depth>=depth){
    if(e.flag==TT_EXACT) return e.score;
    if(e.flag==TT_LOWER && e.score>alpha) alpha=e.score;
    else if(e.flag==TT_UPPER && e.score<beta) beta=e.score;
    if(alpha>=beta) return e.score; ttm=e.best; }
  else if(e.key==key) ttm=e.best;
  vector<Move> mv; legalMoves(mv);
  if(mv.empty()){ if(inCheck(sideToMove)) return -30000+ply; return 0; }
  orderMoves(mv,ttm,ply);
  int best=-100000; Move bm=mv[0];
  for(auto&m:mv){ Undo u; makeMove(m,u); nodes++; int sc=-negamax(depth-1,-beta,-alpha,ply+1); unmakeMove(m,u);
    if(sc>best){best=sc;bm=m;} if(best>alpha)alpha=best;
    if(alpha>=beta){ if(board[m.to]==EMPTY && m.flag!=2){ killers[ply][1]=killers[ply][0]; killers[ply][0]=m; } break; } }
  int flag = best<=alphaOrig?TT_UPPER : best>=beta?TT_LOWER : TT_EXACT;
  if(e.depth<=depth){ e.key=key; e.depth=depth; e.score=best; e.flag=flag; e.best=bm; }
  return best;
}
Move searchBest(int maxDepth){
  ttClear(); for(auto&k:killers){ k[0]={0,0,0,0}; k[1]={0,0,0,0}; }
  Move best{0,0,0,0};
  for(int d=1;d<=maxDepth;d++){ vector<Move> mv; legalMoves(mv); if(mv.empty())break;
    u64 key=hashPos(); Move ttm = (TT[key&TT_MASK].key==key)?TT[key&TT_MASK].best:best;
    int alpha=-100000,beta=100000,bsc=-100000; Move bm=mv[0];
    orderMoves(mv,ttm,0);
    for(auto&m:mv){ Undo u; makeMove(m,u); nodes++; int sc=-negamax(d-1,-beta,-alpha,1); unmakeMove(m,u);
      if(sc>bsc){bsc=sc;bm=m;} if(bsc>alpha)alpha=bsc; }
    best=bm;
    TTE&e=TT[key&TT_MASK]; e.key=key; e.depth=d; e.score=bsc; e.flag=TT_EXACT; e.best=bm; }
  return best;
}
// iterative deepening with a wall-clock budget (ms); TT persists across depths
Move searchTimed(long long budgetMs){
  using namespace std::chrono;
  auto t0=steady_clock::now();
  ttClear(); for(auto&k:killers){ k[0]={0,0,0,0}; k[1]={0,0,0,0}; }
  Move best{0,0,0,0};
  for(int d=1;d<=64;d++){
    vector<Move> mv; legalMoves(mv); if(mv.empty())break;
    u64 key=hashPos(); Move ttm=(TT[key&TT_MASK].key==key)?TT[key&TT_MASK].best:best;
    int alpha=-100000,beta=100000,bsc=-100000; Move bm=mv[0];
    orderMoves(mv,ttm,0);
    for(auto&m:mv){ Undo u; makeMove(m,u); nodes++; int sc=-negamax(d-1,-beta,-alpha,1); unmakeMove(m,u);
      if(sc>bsc){bsc=sc;bm=m;} if(bsc>alpha)alpha=bsc; }
    best=bm;
    TTE&e=TT[key&TT_MASK]; e.key=key; e.depth=d; e.score=bsc; e.flag=TT_EXACT; e.best=bm;
    auto el=duration_cast<milliseconds>(steady_clock::now()-t0).count();
    if(el*2 >= budgetMs) break;   // unlikely to finish another, deeper iteration
  }
  return best;
}

Move parseUci(const string&s){ // e2e4 / e7e8q
  Move m{0,0,0,0}; int from=sq(s[0]-'a',s[1]-'1'), to=sq(s[2]-'a',s[3]-'1'); m.from=from;m.to=to;
  if(s.size()>=5) m.promo=s[4];
  int p=board[from];
  if(typeOf(p)=='p'&&to==epSquare&&epSquare!=-1) m.flag=2;
  if(typeOf(p)=='p'&&abs(rankOf(to)-rankOf(from))==2) m.flag=1;
  if(typeOf(p)=='k'&&(to-from==2)) m.flag=3;
  if(typeOf(p)=='k'&&(from-to==2)) m.flag=4;
  return m;
}

int main(int argc,char**argv){
  initVal(); initZobrist();
  if(argc>=4 && string(argv[1])=="perft"){ setFen(argv[2]); cout<<perft(atoi(argv[3]))<<endl; return 0; }
  // UCI
  string line;
  setFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  while(getline(cin,line)){
    istringstream is(line); string tok; is>>tok;
    if(tok=="uci"){ cout<<"id name QuantumKnight\nid author the village\nuciok\n"<<flush; }
    else if(tok=="isready") cout<<"readyok\n"<<flush;
    else if(tok=="ucinewgame") setFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    else if(tok=="position"){ string w; is>>w; string rest;
      if(w=="startpos"){ setFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"); is>>w; }
      else if(w=="fen"){ string f,a; vector<string> parts; for(int i=0;i<6&&is>>a;i++) parts.push_back(a);
        string ff; for(size_t i=0;i<parts.size();i++){ if(parts[i]=="moves"){ w="moves"; break;} ff+=(i?" ":"")+parts[i]; } setFen(ff);
        if(w!="moves") is>>w; }
      if(w=="moves"){ string mvs; while(is>>mvs){ Move m=parseUci(mvs); Undo u; makeMove(m,u);} }
    }
    else if(tok=="go"){ int depth=-1; long long movetime=-1,wt=-1,bt=-1,winc=0,binc=0; string a;
      while(is>>a){ if(a=="depth"){is>>depth;} else if(a=="movetime"){is>>movetime;}
        else if(a=="wtime"){is>>wt;} else if(a=="btime"){is>>bt;}
        else if(a=="winc"){is>>winc;} else if(a=="binc"){is>>binc;} }
      nodes=0; Move b;
      if(depth>0 && movetime<0 && wt<0) b=searchBest(depth);
      else { long long budget=movetime;
        if(budget<0){ long long clk=(sideToMove==0?wt:bt), inc=(sideToMove==0?winc:binc);
          budget = clk>0 ? clk/30 + inc : 1000; }
        b=searchTimed(budget); }
      cout<<"bestmove "<<moveStr(b)<<"\n"<<flush; }
    else if(tok=="quit") break;
  }
  return 0;
}
