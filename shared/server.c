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
#include  <stdint.h>
#include "switchboard.h"

struct msgq_buf {
    long mtype;
	sbMessage_t msg;
};


int init_write_shm()
{
    key_t          MsgQKEY;
    int            MsgQID = -1;

    if ((MsgQKEY = ftok("/home", 'y')) == -1) {
        return -1; // Need to add and handle proper error code.
    }
    if ((MsgQID = msgget(MsgQKEY, 0666 | IPC_CREAT)) == -1) {
        return -1; // Need to add and handle proper error code.
    }

    return MsgQID;
}

int init_read_shm()
{
    key_t          MsgQKEY;
    int            MsgQID = -1;

    if ((MsgQKEY = ftok("/home", 'x')) == -1) {
        return -1; // Need to add and handle proper error code.
    }
    if ((MsgQID = msgget(MsgQKEY, 0666 | IPC_CREAT)) == -1) {
        return -1; // Need to add and handle proper error code.
    }

    return MsgQID;
}

int is_rbuf_ready_nw(int MsgQID)
{
    struct msqid_ds status;
    if(msgctl(MsgQID, MSG_STAT, &status) == -1) {
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
        return -1;
    }

    sMsg = (sbMessage_t *)&buf.msg;

    memcpy(data, &buf.msg, dataSize);
    return dataSize;
}

int write_shm(char *data, int MsgQID)
{

    struct msgq_buf buf;
    int dataSize;

    buf.mtype = 1;
    sbMessage_t *sMsg = (sbMessage_t *)data;
    
    dataSize = sizeof(sbMessage_t);

    memset(&buf.msg, 0, dataSize);
    memcpy(&buf.msg, data, dataSize);
    if (msgsnd(MsgQID, &buf, dataSize, 0) == -1) {
        return -1;
    }
    return dataSize;
}


int delete_shm(int MsgQID)
{
    if (msgctl(MsgQID, IPC_RMID, NULL) == -1) {
        return -1; // Need to add and handle proper error code
    }
    return 0;
}

