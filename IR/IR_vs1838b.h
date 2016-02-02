/* --------------------------------
 *          IR_vs1838b.h
 * --------------------------------
 * Infrared Receiver Module VS1838b
 * ================================
 *  2015 @ Tsinghua Yizhuang ZHOU
 *
 *  ---------------
 *  |             |
 *  |   /-----\   |
 *  |   |     |   |
 *  |   |     |   |
 *  |   \-----/   |
 *  |             |
 *  ---------------
 *     |   |   |
 *     |   |   |
 *    OUT GND VCC
 *     |    \ /
 *     |     X
 *     |    / \
 *     |   |   |
 *  ---|---|---|---
 *     Y   R   G
 *  ---|---|---|---
 *     |   |   |
 *   P2.0 VCC GND
 *
 * --------------------------------
 * Quick Start:
 *
 * main.c example:
 *

#include "io430.h"
#inlcude "in430.h"
#include "IR_vs1838b.h"

void main() {
    // ......

    IR_init();
    _EINT();
    while(1);
}

void my_func() {
    // Your code here
    // e.g. P1OUT = ~P1OUT;
    //
    // To read data received, try:
    // data_read = IR_buffer[2];
}

#pragma vector = IR_TRIG_VECTOR
__interrupt void Timer1_A0() {
    IR_trig(my_func);
}


 * Then every time IR receives data,
 * my_func() will be executed.
 * You can set breakpoint to check
 * data you received.
 *
 * --------------------------------
 * Note:
 * 1.	Only Pulse Width Modulation
 * 	(PWM) infrared signal can be
 * 	demodulated correctly by now.
 * 2.	ACLK(32768HZ) is required.
 * 	Change settings yourself if
 * 	it is unavailable.
 * 3.	This work's not perfect.
 * 	Fixes and improvements are
 * 	welcomed.
 *
 * --------------------------------
 * PWM signal:
 * 		1.125ms
 * 	bit0: ---    ------
 * 		|    |    |
 * 		|    |    |
 * 		------    ---
 * 		0.56ms
 *
 *              2.25ms
 * 	bit1: ---    --------------
 *       	|    |            |
 * 		|    |            |
 * 		------            ---
 * 		0.56ms
 *
 * --------------------------------
 * Infrared Signal:
 *
 * 	 Leader Code  Custom Code  Data Code  Stop
 * 	|------------|------------|----------||
 *	 13.5ms       2 bytes      2 bytes
 *
 *	 Resend Code  Stop
 *	|------------||
 * 	 11.5ms
 * --------------------------------
 */

#ifndef IR_VS1838B_h
#define IR_VS1838B_h

#include "io430.h"

// Default Pin  : P2.0
// Default Timer: TimerA1.0
// You can change the correlated pin and timer.
#define IR_TRIG_VECTOR	TIMER1_A0_VECTOR
#define IRSEL		P2SEL_bit.P0
#define IRSEL2		P2SEL2_bit.P0
#define IRDIR		P2DIR_bit.P0
#define IRCTL		TA1CTL
#define IRCCTL		TA1CCTL0
#define IRCCR		TA1CCR0

// To imporove the robustness of the system,
// Vertification of Custom Code and Data Code
// is neccessary. However, you may have to
// modify source code yourself cause a differed
// remote control.
#define IR_VERTIFY	0	//Default: FALSE


/* ---------------------- *
 * Varibles and Functions *
 * ---------------------- */

/* Varible: IR_buffer[4]
 * Descrip: The array to keep the latest
 * 	    data the IR module received.
 * Note   : This varible can be visited
 * 	    and modified directly anywhere.
 * 	    Be cautious!
 * 	    (You can wrap this varible up
 * 	    by an extra function to forbid
 * 	    direct visit. If so, remember
 * 	    to comment up the line below.)
 */
extern unsigned char	IR_buffer[4];


/* Func  : IR_init
 * Args  : None
 * Return: None
 * Usage : Init the IR module.
 */
void IR_init();


/* Func  : IR_trig
 * Args  : one function pointer
 * Return: None
 * Usage : This function should be called
 * 	   in the interrupt function of
 * 	   the Timer Module. Like:
 *
 * 	     #pragma vector = IR_TRIG_VECTOR
 * 	     __interrupt void Timer1_A0() {
 * 	     	IR_trig(IR_callfunc);
 * 	     }
 *
 * Note  : Copy the code above to MAIN.C.
 */
void IR_trig(void (*callfunc)());


/* Func	 : IR_callfunc
 * Args  : None
 * Return: None
 * Usage : You can pass this function
 * 	   to IR_trig. Every time IR
 * 	   finishes demodulation, this
 * 	   function will be called.
 *
 * 	   You can create your own
 * 	   function just like this one.
 * Note  :
 *   1.    This function should NOT take
 *   	   much time, for it is called in
 *   	   an interrupt function.
 *
 *   2.	   If you'd like to create a func
 * 	   which takes arguments, modify
 * 	   the IR_trig() function. Like:
 *
 * 	     void IR_trig(void (*callfunc)(int, int));
 *
 *   3.	   If you'd like to return some
 * 	   value, use pointers instead.
 *
 *   4.	   Refer to source file for details.
 */
void IR_callfunc();

#endif
