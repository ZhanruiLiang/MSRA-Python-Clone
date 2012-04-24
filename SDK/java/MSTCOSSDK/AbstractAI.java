package MSTCOSSDK;

public abstract class AbstractAI {
    protected final OSInterface Interface;
    public AbstractAI(OSInterface game){
        Interface = game;
    };
    public abstract void Iteration();
}
