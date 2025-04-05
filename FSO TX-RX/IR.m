clear; clc; close all;

tx_msg = 'Hello World';
ascii_vals = double(tx_msg);
disp('ASCII Codes for each character in "Hello World":');
disp(ascii_vals);

tx_bits = [];  

for iChar = 1:length(ascii_vals)
    charVal = ascii_vals(iChar);
    for b = 0:7
        bitVal = bitget(charVal, b+1); 
        tx_bits = [tx_bits, bitVal];
    end
end

disp('Bit stream (LSB-first for each character):');
disp(tx_bits);

bitrate      = 1000;       
carrier_freq = 38000;     
Fs           = 200000;    
Tb           = 1/bitrate;  

samples_per_bit = round(Tb * Fs);

total_bits     = length(tx_bits);
total_duration = total_bits * Tb;
t             = 0 : 1/Fs : (total_duration - 1/Fs);

carrier = sin(2*pi*carrier_freq * t); 

tx_signal = zeros(size(t));

index_start = 1;
for iBit = 1:total_bits
    bitVal = tx_bits(iBit);
    
    index_end = index_start + samples_per_bit - 1;
    
    if bitVal == 1
        tx_signal(index_start:index_end) = carrier(index_start:index_end);
    else
        tx_signal(index_start:index_end) = 0;
    end
    
    index_start = index_end + 1;
end

figure;
plot(t(1:10*samples_per_bit)*1e3, tx_signal(1:10*samples_per_bit));
xlabel('Time (ms)');
ylabel('Amplitude');
title('Transmitted Signal (First 10 Bits)');

rx_signal = tx_signal; 

reference_carrier = sin(2*pi*carrier_freq * t); 
mixed_signal = rx_signal .* reference_carrier;
demod_bits = zeros(1, total_bits);
idx_start  = 1;

for iBit = 1:total_bits
    idx_end  = idx_start + samples_per_bit - 1;
    bit_chunk = mixed_signal(idx_start:idx_end);
    
    energy = sum(abs(bit_chunk));
    
    threshold = samples_per_bit * 0.4; 

    if energy > threshold
        demod_bits(iBit) = 1;
    else
        demod_bits(iBit) = 0;
    end
    
    idx_start = idx_end + 1;
end

num_chars = length(demod_bits)/8;
rx_ascii = zeros(1, num_chars);  

bit_idx = 1;
for c = 1:num_chars
    byte_val = 0;
    for b = 0:7
        bit_val = demod_bits(bit_idx);
        byte_val = bitset(byte_val, b+1, bit_val);
        bit_idx = bit_idx + 1;
    end
    rx_ascii(c) = byte_val;
end

rx_msg = char(rx_ascii);

disp('Demodulated Bits:');
disp(demod_bits);

disp('Reconstructed ASCII values:');
disp(rx_ascii);

disp('Reconstructed Message:');
disp(rx_msg);

figure;
stem(demod_bits(1:40), 'Marker','none');
xlabel('Bit Index');
ylabel('Bit Value');
title('First 40 Demodulated Bits');
