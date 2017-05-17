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
#include "switchboard.h"

#define  NOT_READY  -1
#define  FILLED     1
#define  TAKEN      0

struct Memory {
	int  status;
	char data[256];
};

int init_write_shm()
{
    key_t          ShmKEY;
    int            ShmID = -1;
    struct Memory *ShmPTR;

    ShmKEY = ftok("/home", 'a');
    ShmID = shmget(ShmKEY, sizeof(struct Memory), IPC_CREAT | 0666);

    ShmPTR = (struct Memory *) shmat(ShmID, NULL, 0);
    memset(ShmPTR, NOT_READY, 256);
    shmdt((void *) ShmPTR);

    return ShmID;
}

int init_read_shm()
{
    key_t          ShmKEY;
    int            ShmID = -1;

    ShmKEY = ftok("/home", 'b');
    ShmID = shmget(ShmKEY, sizeof(struct Memory), IPC_CREAT | 0666);

    return ShmID;
}


int read_shm(char *data, int ShmID)
{
    int dataSize;
    struct Memory  *ShmPTR;
    sbMessage_t *sMsg;

    ShmPTR = (struct Memory *) shmat(ShmID, NULL, 0);

    if (ShmPTR == NULL)
	    return -1;

    while (ShmPTR->status != FILLED)
        continue;

    sMsg = (sbMessage_t *)ShmPTR->data;

    if (sMsg->hdr.message_type == SB_BOARD_INFO_RSP)
        dataSize = SB_BOARD_INFO_RSP_LEN;
    else if (sMsg->hdr.message_type == SB_STATE_CHANGE_RSP)
        dataSize = SB_STATE_CHANGE_RSP_LEN;
    else if (sMsg->hdr.message_type == SB_DEVICE_READY_NTF)
        dataSize = SB_DEVICE_READY_NTF_LEN;
    else
        dataSize = 128;

    memcpy(data, ShmPTR->data, dataSize);
    ShmPTR->status = TAKEN;

    shmdt((void *) ShmPTR);
    return dataSize;
}

int write_shm(char *data, int ShmID)
{
    int dataSize;
    sbMessage_t *sMsg = (sbMessage_t *)data;
    struct Memory  *ShmPTR;

    ShmPTR = (struct Memory *) shmat(ShmID, NULL, 0);

    if (ShmPTR == NULL)
	    return -1;

    if (sMsg->hdr.message_type == SB_BOARD_INFO_REQ)
        dataSize = SB_BOARD_INFO_REQ_LEN;
    else if (sMsg->hdr.message_type == SB_STATE_CHANGE_REQ)
        dataSize = SB_STATE_CHANGE_REQ_LEN;
    else
	    dataSize = 128;

    memset(ShmPTR->data, 0, 256);
    memcpy(ShmPTR->data, data, dataSize);
    ShmPTR->status = FILLED;

    shmdt((void *) ShmPTR);
    return dataSize;
}


int delete_shm(int ShmID)
{
    shmctl(ShmID, IPC_RMID, NULL);
    return 0;
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
