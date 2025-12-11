Some links with resources:
https://unix.stackexchange.com/questions/512759/multiple-dev-video-for-one-physical-device


command: v4l2-ctl --list-devices

Cam Link 4K: Cam Link 4K (usb-0000:03:00.0-1):
	/dev/video0
	/dev/video1
	/dev/media0

Explanation:
The multiple device entries you are seeing for your Cam Link 4K, such as /dev/video0, /dev/video1, 
and /dev/media0, are due to the kernel's video4linux (v4l2) subsystem creating separate device nodes 
for different functionalities of the same physical hardware. Specifically, the uvcvideo driver, 
which handles USB Video Class devices like the Cam Link 4K, can create additional device nodes to 
provide metadata about the video stream, such as timestamps or per-frame data, alongside the primary 
video capture device.

To avoid issues, applications should check the device capabilities using VIDIOC_QUERYCAP to identify 
and use only the devices that support video capture.


command: v4l2-ctl -D -d /dev/video0

Driver Info:
	Driver name      : uvcvideo
	Card type        : Cam Link 4K: Cam Link 4K
	Bus info         : usb-0000:03:00.0-1
	Driver version   : 6.14.11
	Capabilities     : 0x84a00001
		Video Capture
		Metadata Capture
		Streaming
		Extended Pix Format
		Device Capabilities
	Device Caps      : 0x04200001
		Video Capture
		Streaming
		Extended Pix Format

Media Driver Info:
	Driver name      : uvcvideo
	Model            : Cam Link 4K: Cam Link 4K
	Serial           : 00051F06F6000
	Bus info         : usb-0000:03:00.0-1
	Media version    : 6.14.11
	Hardware revision: 0x00000000 (0)
	Driver version   : 6.14.11
Interface Info:
	ID               : 0x03000002
	Type             : V4L Video
Entity Info:
	ID               : 0x00000001 (1)
	Name             : Cam Link 4K: Cam Link 4K
	Function         : V4L2 I/O
	Flags            : default
	Pad 0x01000007   : 0: Sink
	  Link 0x0200000d: from remote pad 0x100000a of entity 'Processing 2' (Video Pixel Formatter): Data, Enabled, Immutable


command: v4l2-ctl -D -d /dev/video1

Driver Info:
	Driver name      : uvcvideo
	Card type        : Cam Link 4K: Cam Link 4K
	Bus info         : usb-0000:03:00.0-1
	Driver version   : 6.14.11
	Capabilities     : 0x84a00001
		Video Capture
		Metadata Capture
		Streaming
		Extended Pix Format
		Device Capabilities
	Device Caps      : 0x04a00000
		Metadata Capture
		Streaming
		Extended Pix Format

Media Driver Info:
	Driver name      : uvcvideo
	Model            : Cam Link 4K: Cam Link 4K
	Serial           : 00051F06F6000
	Bus info         : usb-0000:03:00.0-1
	Media version    : 6.14.11
	Hardware revision: 0x00000000 (0)
	Driver version   : 6.14.11
Interface Info:
	ID               : 0x03000005
	Type             : V4L Video
Entity Info:
	ID               : 0x00000004 (4)
	Name             : Cam Link 4K: Cam Link 4K
	Function         : V4L2 I/O

