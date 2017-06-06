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
#include  <sys/types.h>
#include  <sys/ipc.h>
#include  <sys/msg.h>
#include  <unistd.h>
#include  <string.h>
#include "switchboard.h"

struct msgq_buf {
    long mtype;
    char mtext[256];
};


int init_write_shm()
{
    key_t          MsgQKEY;
    int            MsgQID = -1;

    if ((MsgQKEY = ftok("/home", 'y')) == -1) {
        perror("ftok");
        return -1; // Need to add and handle proper error code.
    }
    if ((MsgQID = msgget(MsgQKEY, 0666 | IPC_CREAT)) == -1) {
        perror("msgget");
        return -1; // Need to add and handle proper error code.
    }

    return MsgQID;
}

int init_read_shm()
{
    key_t          MsgQKEY;
    int            MsgQID = -1;

    if ((MsgQKEY = ftok("/home", 'x')) == -1) {
        perror("ftok");
        return -1; // Need to add and handle proper error code.
    }
    if ((MsgQID = msgget(MsgQKEY, 0666 | IPC_CREAT)) == -1) {
        perror("msgget");
        return -1; // Need to add and handle proper error code.
    }

    return MsgQID;
}

int is_rbuf_ready_nw(int MsgQID)
{
    struct msqid_ds status;
    if(msgctl(MsgQID, MSG_STAT, &status) == -1) {
        perror("msgctl");
        return -1; // Need to add and handle proper error code
    }
    if(status.msg_qnum == 0)
        return 0;
    else
        return 1;

}

int read_shm(char *data, int MsgQID)
{

    struct msgq_buf buf;
    buf.mtype = 0;
    int dataSize;
    sbMessage_t *sMsg;

    dataSize = sizeof(sbMessage_t);
    if (msgrcv(MsgQID, &buf, dataSize, 0, 0) == -1) {
        perror("msgrcv");
        return -1;
    }

    sMsg = (sbMessage_t *)buf.mtext;


    if (sMsg->hdr.message_type == SB_BOARD_INFO_RSP)
    {
        printf("r:board info rsp\n");
    }
    else if (sMsg->hdr.message_type == SB_STATE_CHANGE_RSP)
    {
        printf("r:state change rsp\n");
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_READY_NTF)
    {
        printf("r:device ready notification\n");
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_INFO_NTF)
    {
        printf("r:dev info message.\n");
        printf("C:::r:sizeof sMsg:%lu\n", sizeof(sbMessage_t));
        
        printf("r: message type:%x\n", sMsg->hdr.message_type);
        printf("r: join state  :%x\n", sMsg->data.devInfo.joinState);
        printf("r: sbType      :%x\n", sMsg->data.devInfo.sbType.type);
        printf("r: dev index   :%x\n", sMsg->data.devInfo.devIndex);
        printf("r: ieee addr   :%lx\n", sMsg->data.devInfo.ieeeAddr);
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
    }

    memcpy(data, buf.mtext, dataSize);
    return dataSize;
}

int write_shm(char *data, int MsgQID)
{

    struct msgq_buf buf;
    int dataSize;

    buf.mtype = 1;
    sbMessage_t *sMsg = (sbMessage_t *)data;
    
    dataSize = sizeof(sbMessage_t);

    if (sMsg->hdr.message_type == SB_BOARD_INFO_REQ)
    {
        printf("board info req\n");
    }
    else if (sMsg->hdr.message_type == SB_STATE_CHANGE_REQ)
    {
        printf("w:state change req\n");
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_READY_REQ)
    {
        printf("w:device ready req\n");
    }
    else
    {
        printf("w:unknown message\n");
    }

    memset(buf.mtext, 0, 256);
    memcpy(buf.mtext, data, dataSize);
    if (msgsnd(MsgQID, &buf, dataSize, 0) == -1) {
        perror("msgsnd");
        return -1;
    }
    return dataSize;
}


int delete_shm(int MsgQID)
{
    if (msgctl(MsgQID, IPC_RMID, NULL) == -1) {
        perror("msgctl");
        return -1; // Need to add and handle proper error code
    }
    return 0;
}

#if 0
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

    dataSize = sizeof(sbMessage_t);

    if (sMsg->hdr.message_type == SB_BOARD_INFO_RSP)
    {
        printf("r:board info rsp\n");
    }
    else if (sMsg->hdr.message_type == SB_STATE_CHANGE_RSP)
    {
        printf("r:state change rsp\n");
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_READY_NTF)
    {
        printf("r:device ready notification\n");
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_INFO_NTF)
    {
        printf("r:dev info message.\n");
        printf("C:::r:sizeof sMsg:%lu\n", sizeof(sbMessage_t));
        
        printf("r: message type:%x\n", sMsg->hdr.message_type);
        printf("r: join state  :%x\n", sMsg->data.devInfo.joinState);
        printf("r: sbType      :%x\n", sMsg->data.devInfo.sbType.type);
        printf("r: dev index   :%x\n", sMsg->data.devInfo.devIndex);
        printf("r: ieee addr   :%lx\n", sMsg->data.devInfo.ieeeAddr);
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

    dataSize = sizeof(sbMessage_t);
    if (sMsg->hdr.message_type == SB_BOARD_INFO_REQ)
    {
        printf("board info req\n");
    }
    else if (sMsg->hdr.message_type == SB_STATE_CHANGE_REQ)
    {
        printf("w:state change req\n");
    }
    else if (sMsg->hdr.message_type == SB_DEVICE_READY_REQ)
    {
        printf("w:device ready req\n");
    }
    else
    {
        printf("w:unknown message\n");
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
#endif

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
