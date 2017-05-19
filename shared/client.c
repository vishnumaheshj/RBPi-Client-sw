/* ----------------------------------------------------------------- */
/* PROGRAM  client.c                                                 */
/*    This is the client program.  It can only be started as the     */
/* server says so.  The client requests the same shared memory the   */
/* server established, attaches it to its own address space, takes   */
/* the data, changes the status to TAKEN, detaches the shared memory,*/
/* and exits.                                                        */
/* ----------------------------------------------------------------- */

#include  <stdio.h>
#include  <stdlib.h>
#include  <sys/types.h>
#include  <sys/ipc.h>
#include  <sys/shm.h>

#define  NOT_READY  -1
#define  FILLED     1
#define  TAKEN      0

struct Memory {
	int  status;
	char data[256];
};

void  main(void)
{
     key_t          ShmKEY;
     int            ShmID;
     struct Memory  *ShmPTR;
     
     ShmKEY = ftok("/home", 'x');
     ShmID = shmget(ShmKEY, sizeof(struct Memory), 0666);
     if (ShmID < 0) {
          printf("*** shmget error (client) ***\n");
          exit(1);
     }
     
     ShmPTR = (struct Memory *) shmat(ShmID, NULL, 0);
     if (ShmPTR == NULL) {
          printf("*** shmat error (client) ***\n");
          exit(1);
     }
     printf("   Client has attached the shared memory...\n");
     
     fprintf(stderr, "shmid = %d\n",ShmID);
     while (ShmPTR->status != FILLED)
          ;
     printf("   Client found the data is ready...\n");
     printf("   Client found %x\n", (int)ShmPTR->data[0]);

     ShmPTR->status = TAKEN;
     printf("   Client has informed server data have been taken...\n");
     shmdt((void *) ShmPTR);
     printf("   Client has detached its shared memory...\n");
     printf("   Client exits...\n");
     exit(0);
}

