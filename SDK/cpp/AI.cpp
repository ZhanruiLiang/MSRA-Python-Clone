// #include "MSTCOSSDK.h"
#include "msra.h"
#include <iostream>
#include <cmath>
#include <cstring>
#include <cstdio>
#include <algorithm>
#pragma comment(lib,"MSTCOSSDK.lib")
using namespace std;

vector<ShipInfo> ships,a,b;

float dist(ShipInfo a,ShipInfo b)
{
    return (a.PositionX - b.PositionX) * (a.PositionX - b.PositionX) + (a.PositionY - b.PositionY) * (a.PositionY - b.PositionY);
}

void Iteration(OSInterface* const Interface)
{
    int i, j, k;
    float t, d;
    Interface->Data();
    ships = Interface->Ship;
    a.clear();
    b.clear();
    for (i = 0; i<ships.size(); i++)
    {
        if (ships[i].Faction == Interface->Faction) a.push_back(ships[i]);
        else b.push_back(ships[i]);
    }

    for (i = 0; i < a.size(); i++)
    {
        d = -1;
        k = 0;
        for (j = 0; j < b.size(); j++)
        {
            t = dist(a[i], b[j]);
            if (t < d || d == -1)
            {
                d = t;
                k = j;
            }
        }
        if (b.size() > 0)
        {
            printf("I wanna move\n");
            Interface->MoveTo(a[i].ID, b[k].PositionX+rand()%200-100, b[k].PositionY+rand()%200-100);
            if (d < CannonRange * CannonRange) Interface->Attack(a[i].ID, b[k].ID);
        }
        else Interface->StartMoving(a[i].ID);
    }
}

int main(int argc, char* argv[])
{
    char* temp[2];
    temp[0] = "buaacpp";
    temp[1] = "11.22.33";
    srand(0);
    MSTCOSSDK::StartGame(2, temp, Iteration);
    return 0;
}
