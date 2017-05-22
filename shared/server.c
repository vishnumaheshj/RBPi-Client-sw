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

    ShmKEY = ftok("/home", 'y');
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

    ShmKEY = ftok("/home", 'x');
    ShmID = shmget(ShmKEY, sizeof(struct Memory), IPC_CREAT | 0666);

    return ShmID;
}

int is_rbuf_ready_nw(int ShmID)
{
    int ret;
    struct Memory  *ShmPTR;

    ShmPTR = (struct Memory *) shmat(ShmID, NULL, 0);
    if (ShmPTR == NULL)
    {
	    ret = 0;
    }
	else if (ShmPTR->status == FILLED)
    {
	    ret = 1;
    }
	else
    {
	    ret = 0;
    }

	shmdt((void *) ShmPTR);

	return ret;
}

int read_shm(char *data, int ShmID)
{
    int dataSize;
    struct Memory  *ShmPTR;
    sbMessage_t *sMsg;

    ShmPTR = (struct Memory *) shmat(ShmID, NULL, 0);

    if (ShmPTR == NULL)
	    return -1;

    printf("r:waiting to be filled filled\n");
    while (ShmPTR->status != FILLED)
        continue;
    printf("r:message filled\n");

    sMsg = (sbMessage_t *)ShmPTR->data;

    if (sMsg->hdr.message_type == SB_BOARD_INFO_RSP)
    {
        printf("r:board info rsp\n");
        dataSize = 40;
    }
    else if (sMsg->hdr.message_type == SB_STATE_CHANGE_RSP)
    {
        printf("r:state change rsp\n");
        dataSize = 40;
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_READY_NTF)
    {
        printf("r:device ready notification\n");
        dataSize = SB_DEVICE_READY_NTF_LEN;
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_INFO_NTF)
    {
        dataSize = SB_DEVICE_INFO_NTF_LEN;
	    printf("r:dev info message.\n");
        printf("C:::r:sizeof sMsg:%d\n", sizeof(sbMessage_t));
		
        printf("r: message type:%x\n", sMsg->hdr.message_type);
        printf("r: join state  :%x\n", sMsg->data.devInfo.joinState);
        printf("r: sbType      :%x\n", sMsg->data.devInfo.sbType.type);
        printf("r: dev index   :%x\n", sMsg->data.devInfo.devIndex);
        printf("r: ieee addr   :%llx\n", sMsg->data.devInfo.ieeeAddr);
        printf("r: ep status   :%x\n", sMsg->data.devInfo.epStatus);
        printf("r: switch1     :%x\n", sMsg->data.devInfo.currentState.switch1);
        printf("r: switch2     :%x\n", sMsg->data.devInfo.currentState.switch2);
        printf("r: switch3     :%x\n", sMsg->data.devInfo.currentState.switch3);
        printf("r: switch4     :%x\n", sMsg->data.devInfo.currentState.switch4);
        printf("r: switch5     :%x\n", sMsg->data.devInfo.currentState.switch5);
        printf("r: switch6     :%x\n", sMsg->data.devInfo.currentState.switch6);
        printf("r: switch7     :%x\n", sMsg->data.devInfo.currentState.switch7);
        printf("r: switch8     :%x\n", sMsg->data.devInfo.currentState.switch8);
    }
    else
    {
        printf("r:unknown message\n");
        dataSize = 128;
    }

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
    {
        printf("board info req\n");
        dataSize = SB_BOARD_INFO_REQ_LEN;
    }
    else if (sMsg->hdr.message_type == SB_STATE_CHANGE_REQ)
    {
        printf("w:state change req\n");
        dataSize = SB_STATE_CHANGE_REQ_LEN;
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_READY_REQ)
    {
        printf("w:device ready req\n");
        dataSize = SB_DEVICE_READY_REQ_LEN;
    }
    else
    {
        printf("w:unknown message\n");
	    dataSize = 128;
    }

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
