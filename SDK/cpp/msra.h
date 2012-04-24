//Ocean Scream SDK By LiJiancheng in BUAA MSTC
#pragma once
#include <string>
#include <vector>
#include <sstream>
#include <iostream>
using std::cerr;
#include "PracticalSocket.h"
#ifdef WIN32
  #include <dos.h>         // For socket(), connect(), send(), and recv()
#else
  #include <unistd.h>          // For close()
#endif

using namespace std;
const float MaxArmor = 1000;
const float Acceleration = 10;
const float MaxSpeed = 25;
const float AngularRate = 45;
const float ShipBoundingRadius = 15;
const float IslandBoundingRadius = 32;
const float CannonSpan = 4;
const float CannonAngle = 90;
const float CannonRange = 350;
const float ResourceRadius = 196;
const float ResourceRestoreRate[6] = { 0, 5, 10, 15, 25, 50 };
const int MapWidth = 2048;
const int MapHeight = 2048;
const float RangeOfView = 400;

class Scanner{
    public:
        Scanner(TCPSocket & sock):sock(sock),good(true){}

        string next()throw(SocketException){
            char c;
            good = false;
            while(sock.recv(&c, 1) > 0){
                if(c != ' ' and c != '\n'){
                    buf.push_back(c);
                }else if(buf.size() != 0){
                    good = true;
                    break;
                }
            }
            string bufnew = buf;
            buf.clear();
            cerr << "word:" <<bufnew << endl;
            return bufnew;
        }
        int nextInt()throw(SocketException){
            ss.clear();
            ss << next();
            int result;
            ss >> result;
            return result;
        }
        float nextFloat()throw(SocketException){
            ss.clear();
            ss << next();
            float result;
            ss >> result;
            return result;
        }
        bool nextBool()throw(SocketException){
            string s = next();
            return (s == "True");
        }
    private:
        TCPSocket & sock;
        string buf;
        stringstream ss;
        bool good;
};

class ShipInfo
{
public:
	int ID;
	int Faction;
	float Armor;
	float CooldownRemain[2];
	float CurrentSpeed;
	float DirectionX;
	float DirectionY;
	bool IsBlocked;
	bool IsMoving;
	bool IsRotating;
	float PositionX;
	float PositionY;
	float Rotation;
	float VelocityX;
	float VelocityY;

    void update(Scanner & in);
};

class ResourceInfo
{
public:
	int ID;
	int Faction;
	float PositionX;
	float PositionY;
    void update(Scanner & in);
};

class OSInterface
{
public:
	OSInterface(string host, int port);
	void Data();
	void Attack(int sourceShip, int targetShip);
	void MoveTo(int sourceShip, float x, float y);
	void StartMoving(int ship);
	void StartRotating(int ship,float target);
	void StartRotatingTo(int ship,float x,float y);
	void Stop(int ship);
	void StopMoving(int ship);
	void StopRotating(int ship);
	void Info(string name, string color);
    bool sendInstruction(string cmd, vector<string> & args);
    void update();
	int Faction;
	int TimeLeft;
	vector<ShipInfo> Ship;
	vector<ResourceInfo> Resource;
	bool Running() const{
        return running;
    }

    void update(Scanner & in);
private:
	TCPSocket client;
	bool running;
    Scanner * pScanner;
};

typedef void (*FIteration)(OSInterface* const Interface);
class  MSTCOSSDK
{
public:
	static void StartGame(int argc, const char* argv[], FIteration);
	OSInterface Interface;
private:
	MSTCOSSDK(string host, int port, string name, string color, FIteration Iteration);
    FIteration Iteration;
	void Start();
};
