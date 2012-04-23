/* package MSTCOSSDK; */
import java.io.*;
public class ShipInfo {
    int ID;
    int Faction;
    float Armor;
    float[] CooldownRemain;
    float CurrentSpeed;
    float DirectionX;
    float DirectionY;
    boolean IsBlocked;
    boolean IsMoving;
    boolean IsRotating;
    float PositionX;
    float PositionY;
    float Rotation;
    float VelocityX;
    float VelocityY;
    /* public ShipInfo(int, int, float, float, float, float, float, float, float, float, float, boolean, boolean, boolean, float[]); */
    public ShipInfo(){}
    public void update(StreamTokenizer in) throws IOException{
        int n;
        String attr;
        in.nextToken();
        in.nextToken();
        n = (int)in.nval;
        for(int i = 0; i < n; i++){
            in.nextToken();
            attr = in.sval;
            in.nextToken();
            if(attr.equals("Faction")){
                Faction = (int)in.nval;
            }else if(attr.equals("PositionX")){
                PositionX = (float)in.nval;
            }else if(attr.equals("PositionY")){
                PositionY = (float)in.nval;
            }else if(attr.equals("VelocityX")){
                VelocityX = (float)in.nval;
            }else if(attr.equals("VelocityY")){
                VelocityY = (float)in.nval;
            }else if(attr.equals("DirectionX")){
                DirectionX = (float)in.nval;
            }else if(attr.equals("DirectionY")){
                DirectionY = (float)in.nval;
            }else if(attr.equals("CurrentSpeed")){
                CurrentSpeed = (float)in.nval;
            }else if(attr.equals("IsBlocked")){
                IsBlocked = Boolean.parseBoolean(in.sval);
            }else if(attr.equals("IsRotating")){
                IsRotating = Boolean.parseBoolean(in.sval);
            }else if(attr.equals("IsMoving")){
                IsMoving = Boolean.parseBoolean(in.sval);
            }else if(attr.equals("Rotation")){
                Rotation = (float)in.nval;
            }else if(attr.equals("Armor")){
                Armor = (float)in.nval;
            }else if(attr.equals("CooldownRemain")){
                CooldownRemain = new float[2];
                CooldownRemain[0] = (float)in.nval;
                in.nextToken();
                CooldownRemain[1] = (float)in.nval;
            }else if(attr.equals("CurrentSpeed")){
                CurrentSpeed = (float)in.nval;
            }else if(attr.equals("ID")){
                ID = (int)in.nval;
            }else{
                System.out.println("Unknown attribute: "+attr);
            }
        }
    }
}

