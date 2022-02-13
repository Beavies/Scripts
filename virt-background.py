# modprobe v4l2loopback video_nr=20 card_label="v4l2loopback" exclusive_caps=1
# virt-background -d <device> -b <background image>
import argparse
import cv2
import numpy as np
import pyfakewebcam
import time

# Global variables
DEBUG=False
DEVICE_NAME=''
BGIMAGE_NAME=''
FKDEV_NAME=''
WIDTH = 1280
HEIGHT = 720
CAM = cv2.VideoCapture(30) # just to initialize global var

def parse_options():
    global DEVICE_NAME
    global BGIMAGE_NAME
    global WIDTH
    global HEIGHT
    global FKDEV_NAME
    global DEBUG
    
    parser = argparse.ArgumentParser(description="Cambiar el fondo webcam por diferencias")
    parser.add_argument("-d", "--device", default='/dev/video0', help="Dispositivo webcam")
    parser.add_argument("-b", "--background", help="Imagen de fondo", required=True)
    parser.add_argument("-wi", "--width", help="ancho imagen", default=1280, type=int)
    parser.add_argument("-he", "--height", help="alto imagen", default=720, type=int)
    parser.add_argument("-f", "--fake", help="fake webcamdevice", default='/dev/video20')
    parser.add_argument("-db", "--debug", help="Debug", action="store_true")
    args = parser.parse_args()
    
    DEVICE_NAME  = args.device
    BGIMAGE_NAME = args.background
    WIDTH        = args.width
    HEIGHT       = args.height
    FKDEV_NAME   = args.fake
    DEBUG        = args.debug
    
def configure_cam():
    global CAM
    
    CAM = cv2.VideoCapture(DEVICE_NAME)
    CAM.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    CAM.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    
    
def deallocate():
    global CAM
    
    print("liberando...")
    CAM.release()
    cv2.destroyAllWindows()
    
    
def get_first_image():
    global CAM
    
    print ("STEP 1: Foto de fondo... 10 segundos...")
    time.sleep(10)

    ret, back = CAM.read()
    
    if ret:
        back = cv2.GaussianBlur(back, (5,5),0)
        back = cv2.cvtColor(back, cv2.COLOR_BGR2HSV)
        cv2.imshow('fondo', back)
        cv2.waitKey(5000)
        cv2.destroyAllWindows()
        
        c = input("Imagen de fondo ok? (s/n)")

        if c != "s":
            deallocate()
            exit(-1)
        else:
            return back
    else:
        print ("Error capturando primera imagen")
        deallocate()
        exit(-1)

def get_frame(orig):
        frame = cv2.GaussianBlur(orig, (5,5),0)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = np.zeros(orig.shape, np.uint8)
                
        #quitamos el fondo de la captura
        diferencia = cv2.absdiff(FIRST_IMAGE, frame)
            
        # los pixels parecidos < 50 en algun canal (RGB) -> negro
        # si algun canal se diferencia -> 255 en  ese canal
        _, diferencia = cv2.threshold(diferencia, 50, 255, cv2.THRESH_BINARY)

        
        # convertimos a blanco (255,255,255) si algun pixel es deferenciado del background
        # creamos la mascara
        r,g,b = cv2.split(diferencia)
        diferencia = r+g+b
        diferencia = cv2.merge((diferencia,diferencia,diferencia))
        diferencia = cv2.dilate(diferencia, np.ones((5,5)))
        
#         cv2.imshow('',diferencia)
#         cv2.waitKey(0)
                
        #test fill the gaps
        diferencia = cv2.cvtColor(diferencia, cv2.COLOR_BGR2GRAY)
        contornos,_ = cv2.findContours(diferencia, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contornos:
            if cv2.contourArea(cnt) > 5500:
                cv2.drawContours(mask, [cnt], 0, (255,255,255),-1)
                
#         cv2.imshow('',mask)
#         cv2.waitKey(0)
        
        if DEBUG:
            cv2.imwrite("mascara.jpg", mask)
                
        inv_mask = 255 - mask
        
        res = cv2.bitwise_or(cv2.bitwise_and(orig,mask), cv2.bitwise_and(BGIMAGE,inv_mask))

        # transmitimos
        res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
        
        return res
    
    

####################### MAIN ########################
        

parse_options()

BGIMAGE = cv2.imread(BGIMAGE_NAME)
BGIMAGE = cv2.resize(BGIMAGE, (WIDTH, HEIGHT))

configure_cam()
FIRST_IMAGE = get_first_image()
FAKE_WEBCAM = pyfakewebcam.FakeWebcam(FKDEV_NAME, WIDTH, HEIGHT)

print ("streaming...\n")

try:
    while True:
        ret, frame = CAM.read()
    
        if not ret:
            print ("Error leyendo de la camara\nAbortando...")
            break
        
        FAKE_WEBCAM.schedule_frame(get_frame(frame))
        
        
 
except KeyboardInterrupt:
    pass


deallocate()
exit(0)
