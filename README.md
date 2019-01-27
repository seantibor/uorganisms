# uorganism - Python micro:organisms on the BBC micro:bit

The uorganism, spoken: 'microorganism' (get it?), project helps students understand how genetic information is passed from generation to generation using the [BBC micro:bit](https://www.microbit.org). Each micro:bit holds a single virtual organism that can reproduce with other micro:bits in range using the built-in radio. Using the REPL, students can see how new organisms are created and track how genetic information is passed from parents to offspring.

## Features:
* Persistent storage of organisms between resets and power failures
* Includes lesson worksheet for students to track pedigrees across generations (coming soon)
* Reproduction events between micro:bits using the built-in radio
* REPL output of reproduction events, including parent information
* Teacher micro:bit device code that has:
  * Logging of all radio messages to the REPL for later analysis
  * Remote lock/unlock functionality to prevent unintended reproduction
  * Remote reset of all micro:bits in range to restart simulation at Generation 0
  
## The Organisms
Each micro:bit contains a virtual organism that has simple gender and color traits. These traits can be tracked from generation to generation and allow students to see the effect of dominant and recessive genes on trait expression. Only one virtual organism can live on the micro:bit at any given time and each organism must reach maturity before it can reproduce. 

### Organism Attributes
* ID: A simple hash id that allows for reasonably unique identification.
* Gender: Either XX or XY. Organisms can only reproduce with others of the opposite gender
* Color: Expressed as B and b alleles, i.e. BB, Bb, and bb gene pairs. We call B dominant and b recessive for color. A homozygous recessive pairing of bb alleles results in a Yellow color trait expression. All other homozygous dominant and heterozygous pairings result in a Blue color trait expression.
* P1: Parent 1's ID. None if the organism is from Generation 0
* P2: Parent 2's ID. None if the organism is from Generation 0
* Time: the creation time of the organism in milliseconds from the boot of the micro:bit. Used to determine uniqueness of the organism
* Gen: The generation number of the organism, defined as +1 from the greater of the two parents' generations. E.g. an organism that has parents from Gen 3 and Gen 5 will be labeled as Gen 6.

## Reproduction Events
These organisms reproduce using the micro:bit radio. A reproduction request containing a string representation of the organism is sent out from a micro:bit when the B button is pressed. Any micro:bits in range with an organism of the opposite gender will automatically respond with their own genetic information. Then the sender and all recipients will have a reproduction event that results in a new offspring organism on the host device. The previous organism is culled and the micro:bit will enter a waiting period until the organism reaches maturity and is ready to reproduce again.

### Sequence of Reproduction
1. Upon startup, the micro:bit looks for a saved organism file on the device and loads it into memory. If no file exists, a new organism is created with random Gender and Color traits.
2. The device enters a waiting state until 30-60 seconds have passed. This is indicated by a W displayed on the micro:bit LED matrix. This feature simulates the need for sexual maturity and prevents students from spamming reproduction requests from their device.
3. Once the organism reaches maturity, the micro:bit displays an R on the LED matrix to indicate Ready. In this state, the microbit is actively listening for new reproduction requests.
4. When the user presses the B button on the micro:bit, a request is sent out with the organism's genetic information. The device waits 500 ms for a response before timing out.
5. All devices in range that receive the request will check if the incoming request is of the opposite gender. If so, the receiving devices will then send back a response packet with the organism's genetic information.
6. The receiving device will then spawn a new organism using both parents' genetic information, and the new organism replaces the old organism on the micro:bit.
7. The originating device reads the first response and uses the genetic information to spawn their own offspring.
8. All devices that reproduced will then enter a waiting state again until the organism reaches maturity. 

## Teacher Device
In addition to the micro:bit organism host devices, a teacher device can be used that provides some additional features for managing the devices, including locking the remote devices to prevent accidental reproduction and logging all radio messages for later analysis.

* Press the A button on the teacher device to lock/unlock all micro:bits in range. All devices will show L when Locked.
* Press the B button on the teacher device to reset all micro:bits to generation 0 with random traits
* Connect the teacher device to a computer and log the REPL stream to see radio traffic.

### REPL Screen Logging on MacOS
``` BASH
screen -L /dev/tty.usbmodem14202 115200
```

## Features in Development
* Object-oriented version of organism
* Jupyter notebook simulation of many generations and thousands of organisms

## TODO
* Additional traits
* Better memory management
* Radio log analysis script
* Visualization of pedigree charts