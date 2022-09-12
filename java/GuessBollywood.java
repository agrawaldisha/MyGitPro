import java.util.*;
class GuessBollywood{
   /* static void otp(char alpha,char[] MOVIEARR){
        System.out.println("reached otp");
        int j=0,p=0;
        for(int i=0;i<MOVIEARR.length;i++){
            if(alpha==MOVIEARR[i])
                p=i;
            if(j==p)
                System.out.print(MOVIEARR[p]);
            if(j%2==0 && j!=p)
            System.out.print("_");
            else if(j%2!=0 && j!=p)
            System.out.print(MOVIEARR[j]);
            j++;
        }
    }
    static void INPUT(char[] MNAME,String MOVIE){
        Scanner scan=new Scanner(System.in);
        System.out.println("NO. OF TRIALS : 3");
        System.out.print("ENTER A CHARACTER  ");
        char alpha=scan.next().charAt(0);
        int index=MOVIE.indexOf(alpha);
        System.out.print(index);
    }*/
    
    static void DISPLAY(String MOVIE){
        char MNAME[]=MOVIE.toCharArray();
        char MNAME2[]=MOVIE.toCharArray();
        for(int i=0;i<MNAME.length;i++)
        {
            if(i%2==0){
                MNAME2[i]='_';
                System.out.print("_");
            }

                else
                System.out.print(MNAME[i]);
        }
        Scanner scan=new Scanner(System.in);
        int trials=3;
        int count=0;
        while(trials>0){
            for(char i:MNAME2)
                {
                    if(i=='_')
                    count++;
                }
            if(count==0){
                System.out.println("  -------------------  congrats you won tha game  --------------------");
                break;}
        count=0;
        System.out.println();
        System.out.println("NO. OF TRIALS :"+trials);
        System.out.print("ENTER A CHARACTER  ");
        char alpha=scan.next().charAt(0);
        int index=MOVIE.indexOf(alpha);
        if(index!=-1)
        {
            MNAME2[index]=alpha;
            System.out.println("Great choice");
          for(char i:MNAME2)
          System.out.print(i);
        }
        else{
            System.out.println("wrong choice choose again");
            trials--;
        }
        }
    }
        public static void main(String[] args){
        System.out.println("   ----    GUESS THE MOVIE GAME ------        ");
        String MOVIES[]={ "SINGHAM","RUDRA","RADHE","RUNWAY34","GABBAR","URI","DRONA"};
        Scanner sc=new Scanner(System.in);
        int MOVIENO=0;
        while(MOVIENO>=0){
            DISPLAY(MOVIES[MOVIENO]);
        System.out.println();
        System.out.print("press 1 to countinue or 0 to stop the game");
        int again=sc.nextInt();
        if(again==1)
            MOVIENO++;
        else{
            MOVIENO=-1;
            System.out.println("Thank you for playing");
        }
        }
    }
}