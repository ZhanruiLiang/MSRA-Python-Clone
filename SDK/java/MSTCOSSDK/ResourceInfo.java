/* package MSTCOSSDK; */
import java.io.*;
public class ResourceInfo{
    int ID;
    int Faction;
    float PositionX;
    float PositionY;
    /* public ResourceInfo(int, int, float, float); */
    public ResourceInfo(){};
    public void update(StreamTokenizer in) throws IOException{
        int n;
        String attr, value;
        in.nextToken();
        in.nextToken();
        n = (int)in.nval;
        for(int i = 0; i < n; i++){
            in.nextToken();
            attr = in.sval;
            System.out.println("sval:"+attr);
            in.nextToken();
            System.out.println("nval:"+in.nval);
            if(attr.equals("Faction")){
                Faction = (int)in.nval;
            }else if(attr.equals("PositionX")){
                PositionX = (float)in.nval;
            }else if(attr.equals("PositionY")){
                PositionY = (float)in.nval;
            }else if(attr.equals("ID")){
                ID = (int)in.nval;
            }else{
                System.out.println("Unknown attribute: "+attr);
            }
        }
    }
}

