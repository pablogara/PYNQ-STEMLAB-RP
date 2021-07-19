import pynq
import pynq.lib
import numpy as np
import matplotlib.pyplot as plt

__author__ = "Pablo Garcia"
__email__ = "pablo.garcia31@alu.umh.es"

class Stemlab(pynq.Overlay):
    def __init__(self, bitfile, **kwargs):
        super().__init__(bitfile, **kwargs)
        if self.is_loaded():
            #led initialization
            self.leds = self.ctrl_leds.channel1
            self.leds.setlength(8)
            #digital I/0 initialization
            self.dgio = self.ctrl_io.channel1
            self.dgio.setlength(10)
            self.dgio.trimask = 0b0000011111
            #PWM block initialization
            self.pwm0 = self.PWM_block.PWM_0
            self.pwm1 = self.PWM_block.PWM_1
            self.pwm2 = self.PWM_block.PWM_2
            self.pwm3 = self.PWM_block.PWM_3
            self.pwm4 = self.PWM_block.PWM_4
            self.pwm5 = self.PWM_block.PWM_5
            #DAC slow initialization
            self.dacs0 = self.dac_slow.ctrl_dac1.channel1
            self.dacs0.setlength(24)
            self.dacs1 = self.dac_slow.ctrl_dac2.channel1
            self.dacs1.setlength(24)
            self.dacs2 = self.dac_slow.ctrl_dac3.channel1
            self.dacs2.setlength(24)
            self.dacs3 = self.dac_slow.ctrl_dac4.channel1
            self.dacs3.setlength(24)
            #ADC slow initialization
            self.xadc = self.xadc_block.ctrl_xadc.channel1
            self.xadc.setlength(1)
            self.fifo_xadc_full = self.xadc_block.ctrl_xadc.channel2
            self.fifo_xadc_full.setlength(1)
            self.dma_xadc = self.xadc_block.axi_dma_0
            #ADC fast initialization
            self.adc = self.adc_block.ctrl_scope.channel1
            self.adc.setlength(1)
            self.fifo_adc_full = self.adc_block.ctrl_scope.channel2
            self.fifo_adc_full.setlength(1)
            self.dma_adc = self.axi_dma_0
    
    def Dg_Out(self, out= 0b00000):
        out_full = out<<5
        self.dgio.write(out_full, 0b1111111111)
    
    def Dg_In(self, full= False):
        read = self.dgio.read()
        if full == False:
            return read & 0b0000011111
        else:
            return read
        
    def PWM(self, n=0, power= False, freq= 0, duty= 0): #freq ~1MHz max, duty=0-1
        CTRL_OFFSET = 0x0
        FREQ_OFFSET = 0x8
        DUTY_OFFSET = 0x40
        
        if n == 0:
            if power == False:
                self.pwm0.write(CTRL_OFFSET, 0)
            else:
                val = 125_000_000/freq
                self.pwm0.write(FREQ_OFFSET, int(val))
                self.pwm0.write(DUTY_OFFSET, int(val*duty))
                self.pwm0.write(CTRL_OFFSET, 1)
        elif n == 1:
            if power == False:
                self.pwm1.write(CTRL_OFFSET, 0)
            else:
                val = 125_000_000/freq
                self.pwm1.write(FREQ_OFFSET, int(val))
                self.pwm1.write(DUTY_OFFSET, int(val*duty))
                self.pwm1.write(CTRL_OFFSET, 1)
        elif n == 2:
            if power == False:
                self.pwm2.write(CTRL_OFFSET, 0)
            else:
                val = 125_000_000/freq
                self.pwm2.write(FREQ_OFFSET, int(val))
                self.pwm2.write(DUTY_OFFSET, int(val*duty))
                self.pwm2.write(CTRL_OFFSET, 1)
        elif n == 3:
            if power == False:
                self.pwm3.write(CTRL_OFFSET, 0)
            else:
                val = 125_000_000/freq
                self.pwm3.write(FREQ_OFFSET, int(val))
                self.pwm3.write(DUTY_OFFSET, int(val*duty))
                self.pwm3.write(CTRL_OFFSET, 1)
        elif n == 4:
            if power == False:
                self.pwm4.write(CTRL_OFFSET, 0)
            else:
                val = 125_000_000/freq
                self.pwm4.write(FREQ_OFFSET, int(val))
                self.pwm4.write(DUTY_OFFSET, int(val*duty))
                self.pwm4.write(CTRL_OFFSET, 1)
        elif n == 5:
            if power == False:
                self.pwm5.write(CTRL_OFFSET, 0)
            else:
                val = 125_000_000/freq
                self.pwm5.write(FREQ_OFFSET, int(val))
                self.pwm5.write(DUTY_OFFSET, int(val*duty))
                self.pwm5.write(CTRL_OFFSET, 1)
        else:
            raise Exception("PWM number out of range. Especify a PWM number in range 0 to 5.")
            
            
    def DAC_slow(self, n=0, power= False, value= 0):
        OUTPUT_MASK = 0b111111111111111111111111
        if power == False:
            calibration = 0b0
        else:
            val = value*2496/1.8
            main_calibration = int(val/16)
            sec_calibration_aux = round(((val/16)-int(val/16))*16)
            sec_calibration = 0b1111111111111111
            calibration = main_calibration<<16 | sec_calibration>>(16-sec_calibration_aux)
        
        if n == 0:
            self.dacs0.write(calibration, OUTPUT_MASK)
        elif n ==1:
            self.dacs1.write(calibration, OUTPUT_MASK)
        elif n ==2:
            self.dacs2.write(calibration, OUTPUT_MASK)
        elif n ==3:
            self.dacs3.write(calibration, OUTPUT_MASK)
        else:
            raise Exception("DAC slow number out of range. Especify a DAC number in range 0 to 3")
    
    
    def ADC_slow(self, channels =[0, 1, 2, 3], grid= False):
        t = []
        datos = []
        datos_s = []
        canal = []
        medidas = []
        
        for i in range(1022):
            t.append(i*400/100)
        
        input_buffer = pynq.allocate(shape=(256,), dtype= np.uint32)
        
        self.xadc.write(1, 0b1)
        while True:
            if self.fifo_xadc_full.read() == 1:
                break
        self.xadc.write(0, 0b1)
        
        for i in range(16):
            self.dma_xadc.recvchannel.transfer(input_buffer)
            self.dma_xadc.recvchannel.wait()
            datos =  datos + input_buffer.tolist()
            
        input_buffer.freebuffer()
        
        for i in range(8, len(datos)):
            canal.append(np.int16((datos[i] & 0xffff0000)/0b10000000000000000))
            medidas.append(np.int16(datos[i] & 0x0000ffff))
        
        Vaux0 = []
        Vaux1 = []
        Vaux8 = []
        Vaux9 = []
        
        
        for j in range(len(medidas)):
            if canal[j]==16:
                Vaux0.append((medidas[j])/9400)
            elif canal[j]==17:
                Vaux1.append((medidas[j])/9400)
            elif canal[j]==24:
                Vaux8.append((medidas[j])/9400)
            elif canal[j]==25:
                Vaux9.append((medidas[j])/9400)
            else:
                raise Exception("Error in data assignment")
                
        V0 = [t, Vaux0]
        V1 = [t, Vaux1]
        V8 = [t, Vaux8]
        V9 = [t, Vaux9]
        
        for i in channels:
            if not(i in [0, 1, 2, 3]):
                raise Exception("Channel numbers out of range. Especify all channel numbers in range 0 to 3.")
        
        plt.figure(figsize=(9.5,8))
        if grid == True:
            plt.grid()
        if 0 in channels:
            plt.plot(t, Vaux8, color= 'tab:blue', label= 'Channel 0')
        if 1 in channels:
            plt.plot(t, Vaux0, color= 'tab:red', label= 'Channel 1')
        if 2 in channels:
            plt.plot(t, Vaux1, color= 'tab:green', label= 'Channel 2')
        if 3 in channels:
            plt.plot(t, Vaux9, color= 'purple', label= 'Channel 3')
        plt.legend(loc= 'lower right')
        plt.ylabel('V')
        plt.xlabel('us')
        plt.ion()
        
        return [V0, V1, V8, V9]
        
        
    def ADC(self, channels= [0, 1], grid= False):
        
        t = []
        for i in range(32768):
            t.append(i*(20/2500))
        
        self.adc.write(1, 0b1)
        while True:
            if self.fifo_adc_full.read() == 1:
                break
        self.adc.write(0, 0b1)
        
        input_buffer = pynq.allocate(shape=(256,), dtype= np.int32)
        
        data = []
        
        for i in range(128):
            self.dma_adc.recvchannel.transfer(input_buffer)
            self.dma_adc.recvchannel.wait()
            data =  data + input_buffer.tolist()
        
        input_buffer.freebuffer()
        
        d1 = []
        d2 = []
        
        for i in data:
            d2.append((np.int16((i & 0xffff0000)/0b10000000000000000))/7686)
            d1.append((np.int16(i & 0x0000ffff))/7686)
        
        for i in channels:
            if not(i in [0, 1]):
                raise Exception("Channel numbers out of range. Especify all channel numbers in range 0 to 1.")
        
        C0 = [t[8:], d1[8:]]
        C1 = [t[8:], d2[8:]]
        
        plt.figure(figsize=(9.5,8))
        if grid == True:
            plt.grid()
        if 0 in channels:
            plt.plot(t[8:], d1[8:], color= 'tab:orange', label= 'Channel 0')
        if 1 in channels:
            plt.plot(t[8:], d2[8:], color= 'tab:blue', label= 'Channel 1')
        plt.legend(loc= 'lower right')
        plt.ylabel('V')
        plt.xlabel('us')
        plt.ion()
        plt.show()
        
        return [C0, C1]
        
    def DAC(self, samples_ch0 = [0], samples_ch1 = [0]):
        
        output = []
        
        if len(samples_ch0) >= len(samples_ch1):
            for i in range(len(samples_ch0)):
                if i < len(samples_ch1):
                    output.append(np.uint32(samples_ch0[i] | samples_ch1[i]<<16))
                else:
                    output.append(np.uint32(samples_ch0[i]))
        else:
            for i in range(len(samples_ch1)):
                if i < len(samples_ch0):
                    output.append(np.uint32(samples_ch0[i] | samples_ch1[i]<<16))
                else:
                    output.append(np.uint32(samples_ch1[i]<<16))
                    
        output_buffer = pynq.allocate(shape=(len(output),), dtype= np.uint32)
        
        np.copyto(output_buffer, output)
        
        self.axi_dma_0.sendchannel.transfer(output_buffer)
        self.axi_dma_0.sendchannel.wait()
        
        output_buffer.freebuffer()
    
            
            
       