using CP;

// Wymiary klastrów zaczytywane z pliku danych .dat
int BlockHeight = ...; // Wysokość podbloku na planszy
int BlockWidth = ...;  // Szerokość podbloku na planszy
int N = BlockHeight * BlockWidth; // Rozmiar planszy

range Size = 1..N;

int numCages = ...; // ilość klatek killer sudoku na planszy
range CagesRange = 1..numCages;

int cageID[Size][Size] = ...;      // indeksy pól w klatce
int cageTarget[CagesRange] = ...;  // suma w klatce

// Zmienna decyzyjna - wybór liczby na daną pozycję na planszy
dvar int board[Size][Size] in 1..N;

subject to {
    // 1. STANDARDOWE OGRANICZENIA SUDOKU
    
    // Unikalność w wierszach
    forall(i in Size, j1 in Size, j2 in Size : j1 < j2)
        board[i][j1] != board[i][j2];
        
    // Unikalność w kolumnach
    forall(j in Size, i1 in Size, i2 in Size : i1 < i2)
        board[i1][j] != board[i2][j];
        
    // Unikalność w podblokach (BlockHeight x BlockWidth)
    forall(r in 0..(N div BlockHeight - 1), c in 0..(N div BlockWidth - 1))
        forall(a1 in 1..BlockHeight, b1 in 1..BlockWidth, a2 in 1..BlockHeight, b2 in 1..BlockWidth : (a1 < a2) || (a1 == a2 && b1 < b2))
            board[BlockHeight*r + a1][BlockWidth*c + b1] != board[BlockHeight*r + a2][BlockWidth*c + b2];

    // 2. OGRANICZENIA KILLER SUDOKU
	forall(k in CagesRange) {
	    forall(i1, j1, i2, j2 in Size : i1 != i2 || j1 != j2) {
	        if (cageID[i1][j1] == k && cageID[i2][j2] == k) {
	            board[i1][j1] != board[i2][j2];
	        }
	    }
	}
}

// ładny print w konsoli
execute {
    writeln("ROZWIAZANIE KILLER SUDOKU (", N, "x", N, "):");
    for(var i=1; i<=N; i++) {
        for(var j=1; j<=N; j++) {
            if(board[i][j] < 10) write(" "); 
            write(board[i][j] + " ");
            
            if(j % BlockWidth == 0 && j < N) write("| ");
        }
        writeln();
        if(i % BlockHeight == 0 && i < N) {
            for(var k=1; k <= (N*3 + (N/BlockWidth)*2); k++) write("-");
            writeln();
        }
    }
}