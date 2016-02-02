/* --------------------------------
 *          IR_vs1838b.c
 * --------------------------------
 * Infrared Receiver Module VS1838b
 * ================================
 *  2015 @ Tsinghua Yizhuang ZHOU
 */

#include "IR_vs1838b.h"

#define	uchar	unsigned char
#define uint	unsigned int
#define BOOL	int
#define TRUE	1
#define FALSE	0

#define IR_1500us	49	// threshold for 1 and 0
#define IR_4000us	131	// threshold for Leader and Resend

uchar 	IR_buffer[4];		// data stores here

uchar 	_IR_byte = 0;		// temp space for data
uint 	_IR_old_cap = 0;	// previous P-edge
uint	_IR_new_cap = 0;	// current  P-edge
uint	_IR_interval = 0;	// time interval between 2 edges
uint	_IR_i = 0;		// count for bits
uint	_IR_j = 0;		// count for bytes
BOOL	_IR_read = FALSE;	// whether a Leader Code detected


/* Function: get the time interval between 2 Positive-Edges,
 * 	     to determine whether it's a Leader Code or
 * 	     Resend Code, and whether it's bit 1 or bit 0.
 */
void _IR_get_interval() {
    if (_IR_new_cap >= _IR_old_cap)
	_IR_interval = _IR_new_cap - _IR_old_cap;
    else
	_IR_interval = _IR_new_cap + 65536 - _IR_old_cap;
}

/* Function: Vertify function to make sure if the data you received
 * 	     is VALID. You can change according to your remote control.
 */
BOOL _IR_vertify() {
    uchar* ib = IR_buffer;
    return (ib[2]+ib[3]==ib[0]+ib[1]);
}


void IR_init() {
    IRSEL = 1; IRSEL2 = 0; IRDIR = 0;
    // Capture/Compare Module; Input
    IRCTL = TACLR + TASSEL_1 + MC_2;
    // TACLR	Clear Timer
    // TASSEL_1	Source: ACLK
    // MC_2	Continious Mode (0FFFFh)
    TA1CCTL0 = CM_1 + SCS + CCIS_0 + CAP + CCIE;
    // CM_1	Capture Mode: Postive Edge
    // SCS	Sync Clock
    // CCIS_0	Source A
    // CAP	Capture Mode
    // CCIE	Enable interrupts
}

void IR_trig(void (*callfunc)()) {
    _IR_new_cap = IRCCR;	// mark current moment
    _IR_get_interval();		// calculate time interval
    if (_IR_read) {
	if (_IR_interval > IR_1500us)
	    _IR_byte |= BIT1;	// received bit 1
	else
	    _IR_byte &= ~BIT1;	// received bit 0
	_IR_byte <<= 1;
	_IR_i++;
	if (_IR_i == 8) {
	    _IR_i = 0;
	    IR_buffer[_IR_j] = _IR_byte;
	    _IR_j++;
	    if (_IR_j == 4) {
		_IR_j = 0;	// all 4 bytes received
		_IR_read=FALSE;

		// === call function ===
		if (IR_VERTIFY) {
		    if (_IR_vertify()) (*callfunc)();
		}else{
		    (*callfunc)();
		}
	    }
	}
    }
    if (_IR_interval > IR_4000us && _IR_interval < 2*IR_4000us)
	_IR_read = TRUE;	// Leader Code captured
    _IR_old_cap = _IR_new_cap;	// prepare for next P-edge
}

void IR_callfunc() {
    unsigned char IR_data = IR_buffer[2];
    // You can set a break point here to
    // see the CODE of each bottom and
    // the Custom Code of the remote control.
    switch (IR_data) {
	case 0x00: break; 	// e.g. Turn light on
	case 0x10: break; 	// e.g. Turn light off
	case 0x20: break;
	case 0x40: break;
    }
}
