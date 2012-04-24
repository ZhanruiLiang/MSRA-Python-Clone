Objects=AI.o msra.o PracticalSocket.o
FLAG=-g

AI: $(Objects)
	g++ $(Objects) $(FLAG) -o AI 

AI.o: AI.cpp msra.h 
	g++ -c $(FLAG) AI.cpp 

msra.o: msra.h msra.cpp
	g++ -c $(FLAG) msra.cpp

PracticalSocket.o: PracticalSocket.cpp PracticalSocket.h
	g++ -c $(FLAG) PracticalSocket.cpp
