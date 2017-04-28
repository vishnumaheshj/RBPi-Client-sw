/* ----------------------------------------------------------------- */
/* PROGRAM  server.c                                                 */
/*    This program serves as the server similar to the one in shm.c. */
/* The difference is that the client is no more a child process.     */
/* Thus, some mechanism must be established between the server and   */
/* the client.  This program uses a naive one.  The shared memory    */
/* has an indicator whose possible values are NOT_READY, FILLED and  */
/* TAKEN.  Before the server completes filling data, the status is   */
/* NOT_READY, after filling data it is FILLED.  Then, the server just*/
/* wait (busy waiting) until the status becomes TAKEN.               */
/*    Note that the server must be started first.  The client can    */
/* only be started as the server says so.  Otherwise, the client may */
/* not be able to use the shared memory of the data therein.         */
/* ----------------------------------------------------------------- */

#include  <stdio.h>
#include  <stdlib.h>
#include  <sys/types.h>
#include  <sys/ipc.h>
#include  <sys/shm.h>
#include  <unistd.h>
#include  <string.h>

#define  NOT_READY  -1
#define  FILLED     0
#define  TAKEN      1

struct Memory {
	int  status;
	char data[50];
};

int init_shm()
{
     key_t          ShmKEY;
     int            ShmID = -1;

     ShmKEY = ftok("/home", 'x');
     ShmID = shmget(ShmKEY, sizeof(struct Memory), IPC_CREAT | 0666);

     return ShmID;
}

int update_shm(char *data, int ShmID)
{
     struct Memory  *ShmPTR;
     ShmPTR = (struct Memory *) shmat(ShmID, NULL, 0);
	

     if (ShmPTR == NULL)
	     return -1;

     memset(ShmPTR->data, 0, 50);
     //fprintf(stdout, "Data %s\n", ShmPTR->data);
     memcpy(ShmPTR->data, data, strlen(data));
     //fprintf(stdout, "Data %s\n", ShmPTR->data);
     ShmPTR->status = FILLED;

     shmdt((void *) ShmPTR);
     return 0;
}

int delete_shm(int ShmID)
{

     shmctl(ShmID, IPC_RMID, NULL);
}


#if 0
void  main(int  argc, char *argv[])
{
	int id; 

	id = init_shm();

	update_shm(argv[1], id);

	while(1)
		continue;
}
#endif
