/* package MSTCOSSDK; */
import java.io.*;
import java.util.Scanner;
public class ResourceInfo{
    int ID;
    int Faction;
    float PositionX;
    float PositionY;
    /* public ResourceInfo(int, int, float, float); */
    public ResourceInfo(){};
    public void update(Scanner in) throws IOException{
        int n;
        String attr, value;
        in.next();
        n = in.nextInt();
        for(int i = 0; i < n; i++){
            attr = in.next();
            if(attr.equals("Faction")){
                Faction = in.nextInt();
            }else if(attr.equals("PositionX")){
                PositionX = in.nextFloat();
            }else if(attr.equals("PositionY")){
                PositionY = in.nextFloat();
            }else if(attr.equals("ID")){
                ID = in.nextInt();
            }else{
                System.out.println("Unknown attribute: "+attr);
            }
        }
    }
}

