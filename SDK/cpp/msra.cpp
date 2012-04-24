#include "msra.h"
#include<iostream>
#include<cmath>
#include<string>
#include<cstring>
#include<cctype>
using std::cerr;
using std::cout;
using std::endl;
using std::string;

void print(string s){
    cerr << s << endl;
}

char _buf[30];

// These two function comes from:
// http://www.jb.man.ac.uk/~slowe/cpp/itoa.html
void strreverse(char* begin, char* end) {
    char tmp;
    while(begin < end){
        tmp = *begin; *begin = *end; *end = tmp;
        begin++; end--;
    }
}

char* itoa( int value, char* result, int base ) {
		// check that the base if valid
		if (base < 2 || base > 16) { *result = 0; return result; }
	
		char* out = result;
		int quotient = abs(value);
	
		do {
			const int tmp = quotient / base;
			*out = "0123456789abcdef"[ quotient - (tmp*base) ];
			++out;
			quotient = tmp;
		} while ( quotient );
	
		// Apply negative sign
		if ( value < 0) *out++ = '-';
	
		strreverse(result, out-1);
		*out = 0;
		return result;
}

string operator+(const string & s, int x){
    string ans = s + itoa(x, _buf, 10);
    return ans;
}

void ResourceInfo::update(Scanner & in){
    string attr, value;
    in.next();
    int n = in.nextInt();
    for(int i = 0; i < n; i++){
        attr = in.next();
        if(attr == ("Faction")){
            Faction = in.nextInt();
        }else if(attr == ("PositionX")){
            PositionX = in.nextFloat();
        }else if(attr == ("PositionY")){
            PositionY = in.nextFloat();
        }else if(attr == ("ID")){
            ID = in.nextInt();
        }else{
            print("Unknown attribute: "+attr);
        }
    }
}
void ShipInfo::update(Scanner & in){
    int n;
    string attr;
    in.next();
    n = in.nextInt();
    for(int i = 0; i < n; i++){
        attr = in.next();
        if(attr == ("Faction")){
            Faction = in.nextInt();
        }else if(attr == ("PositionX")){
            PositionX = in.nextFloat();
        }else if(attr == ("PositionY")){
            PositionY = in.nextFloat();
        }else if(attr == ("VelocityX")){
            VelocityX = in.nextFloat();
        }else if(attr == ("VelocityY")){
            VelocityY = in.nextFloat();
        }else if(attr == ("DirectionX")){
            DirectionX = in.nextFloat();
        }else if(attr == ("DirectionY")){
            DirectionY = in.nextFloat();
        }else if(attr == ("CurrentSpeed")){
            CurrentSpeed = in.nextFloat();
        }else if(attr == ("IsBlocked")){
            IsBlocked = in.nextBool();
        }else if(attr == ("IsRotating")){
            IsRotating = in.nextBool();
        }else if(attr == ("IsMoving")){
            IsMoving = in.nextBool();
        }else if(attr == ("Rotation")){
            Rotation = in.nextFloat();
        }else if(attr == ("Armor")){
            Armor = in.nextFloat();
        }else if(attr == ("CooldownRemain")){
            CooldownRemain[0] = in.nextFloat();
            CooldownRemain[1] = in.nextFloat();
        }else if(attr == ("CurrentSpeed")){
            CurrentSpeed = in.nextFloat();
        }else if(attr == ("ID")){
            ID = in.nextInt();
        }else{
            print("Unknown attribute: "+attr);
        }
    }
}

void parseRGB(string rgb, int & r, int & g, int & b){
    int i;
    int j;
    int *p;
    int * ps[3] = {&r, &g, &b};
    i = 0;

    for(int j = 0; j < 3; j++){
        p = ps[j];
        *p = 0;
        for(*p = 0; i < rgb.size() and rgb[i] != '.'; i++){
            *p = *p * 10 + (i - '0');
        }
    }
}

void MSTCOSSDK::StartGame(int argc, const char* argv[], FIteration Iteration){
    string host;
    int port;
    host = "localhost";
    port = 55001;

    MSTCOSSDK sdk(host, port, argv[0], argv[1], Iteration);
    sdk.Start();
}

MSTCOSSDK::MSTCOSSDK(string host, int port, string name, string color, FIteration Iteration):
            Interface(host, port), Iteration(Iteration){
                Interface.Info(name, color);
            }

void MSTCOSSDK::Start(){
    OSInterface * pGame = &Interface;
    // int r, g, b;
    // parseRGB(color, r, g, b);
    if(pGame->Running()){
        pGame->Data();
        while(pGame->Running()){
            Iteration(pGame);
        }
    }
}

OSInterface::OSInterface(string host, int port){
    while(1){
        try{
            client.connect(host, port);
            cout << "Connected to server " << client.getForeignAddress() << endl;
            pScanner = new Scanner(client);
            running = 1;
            break;
        }catch(SocketException e){
            cout << "server not ready yet\n";
            sleep(1);
        }
    }
}

bool OSInterface::sendInstruction(string cmd, vector<string> & args){
    stringstream ss;
    ss << cmd;
    ss << " 0";
    print("Args size:"+args.size());
    for(int i = 0; i < args.size(); i++){
        ss << " " << args[i] ;
    }
    ss << "\n";
    const string & inst = ss.str();
    print("Sending "+inst);
    try{
        client.send((const char*)inst.c_str(), inst.size());
        // client.flush();
    }catch(SocketException e){
        print("Connection lost.");
        running = false;
        return false;
    }
    return true;
}

void OSInterface::Info(string name, string color){
    vector<string> args;
    args.push_back(name);
    args.push_back(color);
    sendInstruction("Info", args);
}

void OSInterface::Data(){
    vector<string> args;
    if(sendInstruction("Data", args)){
        try{
            update();
        }catch(SocketException e){
            print(e.what());
            print("error, data can not be updated.");
            running = false;
        }
    }
}

void OSInterface::update(){
    string attr, value;
    Scanner & in = *pScanner;
    in.next();
    int n = in.nextInt();
    for(int i = 0; i < n; i++){
        attr = in.next();
        if(attr == ("Faction")){
            Faction = in.nextInt();
        }else if(attr == ("Running")){
            running = in.nextBool();
        }else if(attr == "TimeLeft"){
            TimeLeft = in.nextInt();
        }else if(attr == ("Resource")){
            int n1 = in.nextInt();
            Resource.clear();
            for(int j = 0; j < n1; j++){
                ResourceInfo r;
                r.update(in);
                Resource.push_back(r);
            }
        }else if(attr == ("Ship")){
            int n1 = in.nextInt();
            Ship.clear();
            for(int j = 0; j < n1; j++){
                ShipInfo ship;
                ship.update(in);
                Ship.push_back(ship);
            }
        }else{
            print("Unknown attribute: "+attr);
        }
    }
}

void OSInterface::Attack(int sourceShip, int targetShip){
    vector<string> args;
    args.push_back(string()+sourceShip);
    args.push_back(string()+targetShip);
    sendInstruction("Attack", args);
}
void OSInterface::MoveTo(int sourceShip, float x, float y){
    vector<string> args;
    args.push_back(string()+sourceShip);
    args.push_back(string()+x);
    args.push_back(string()+y);
    sendInstruction("MoveTo", args);
}
void OSInterface::StartMoving(int ship){
    vector<string> args;
    args.push_back(string()+ship);
    sendInstruction("StartMoving", args);
}
void OSInterface::StartRotating(int ship, float target){
    vector<string> args;
    args.push_back(string()+ship);
    args.push_back(string()+target);
    sendInstruction("StartRotating", args);
}
void OSInterface::StartRotatingTo(int ship, float x, float y){
    vector<string> args;
    args.push_back(string()+ship);
    args.push_back(string()+x);
    args.push_back(string()+y);
    sendInstruction("StartRotatingTo", args);
}
void OSInterface::Stop(int ship){
    vector<string> args;
    args.push_back(string()+ship);
    sendInstruction("", args);
}
void OSInterface::StopMoving(int ship){
    vector<string> args;
    args.push_back(string()+ship);
    sendInstruction("StopMoving", args);
}
void OSInterface::StopRotating(int ship){
    vector<string> args;
    args.push_back(string()+ship);
    sendInstruction("StopRotating", args);
}
