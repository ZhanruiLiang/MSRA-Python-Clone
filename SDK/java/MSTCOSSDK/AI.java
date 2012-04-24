package MSTCOSSDK;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class AI extends AbstractAI {
	public AI(OSInterface Interface) {
		super(Interface);
	}
	
	List<ShipInfo> ships,a,b;
	Random random = new Random();
	float d;
	int k;
	
	private float dist(ShipInfo a, ShipInfo b)
	{
		return (a.PositionX - b.PositionX) * (a.PositionX - b.PositionX) + (a.PositionY - b.PositionY) * (a.PositionY - b.PositionY);
	}
	
	@Override
	public void Iteration()
	{
		Interface.Data();
		ships = Interface.Ship;
		a = new ArrayList<ShipInfo>();
		b = new ArrayList<ShipInfo>();
		for (int i = 0; i < ships.size(); i++)
			if (ships.get(i).Faction == Interface.Faction) a.add(ships.get(i));
			else b.add(ships.get(i));
		
		for (int i = 0; i < a.size(); i++)
		{
			d = -1;
			for (int j = 0; j < b.size(); j++)
			{
				float t = dist(a.get(i), b.get(j));
				if (t < d || d == -1)
				{
					d = t;
					k = j;
				}
			}
			
			if (b.size()>0)
			{
				Interface.MoveTo(a.get(i).ID, b.get(k).PositionX+(float)(random.nextDouble() - 0.5) * 200f, b.get(k).PositionY+(float)(random.nextDouble() - 0.5) * 200f);
				if (d < OSInterface.CannonRange * OSInterface.CannonRange) Interface.Attack(a.get(i).ID, b.get(k).ID);
			}
			else Interface.StartMoving(a.get(i).ID);
		}
	}
	
	public static void main(String args[])
	{
		String[] temp =new String[2];
		temp[0] = "buaajava";
		temp[1] = "111.22.33";
		SDK.StartGame(temp);
	}
}