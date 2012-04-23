/* package MSTCOSSDK; */
import java.io.*;
import java.util.Scanner;
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
    public void update(Scanner in) throws IOException{
        int n;
        String attr;
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
            }else if(attr.equals("VelocityX")){
                VelocityX = in.nextFloat();
            }else if(attr.equals("VelocityY")){
                VelocityY = in.nextFloat();
            }else if(attr.equals("DirectionX")){
                DirectionX = in.nextFloat();
            }else if(attr.equals("DirectionY")){
                DirectionY = in.nextFloat();
            }else if(attr.equals("CurrentSpeed")){
                CurrentSpeed = in.nextFloat();
            }else if(attr.equals("IsBlocked")){
                /* IsBlocked = in.nextBoolean(); */
                IsBlocked = Boolean.parseBoolean(in.next());
            }else if(attr.equals("IsRotating")){
                IsRotating = Boolean.parseBoolean(in.next());
            }else if(attr.equals("IsMoving")){
                IsMoving = Boolean.parseBoolean(in.next());
            }else if(attr.equals("Rotation")){
                Rotation = in.nextFloat();
            }else if(attr.equals("Armor")){
                Armor = in.nextFloat();
            }else if(attr.equals("CooldownRemain")){
                CooldownRemain = new float[2];
                CooldownRemain[0] = in.nextFloat();
                CooldownRemain[1] = in.nextFloat();
            }else if(attr.equals("CurrentSpeed")){
                CurrentSpeed = in.nextFloat();
            }else if(attr.equals("ID")){
                ID = in.nextInt();
            }else{
                System.out.println("Unknown attribute: "+attr);
            }
        }
    }
}

