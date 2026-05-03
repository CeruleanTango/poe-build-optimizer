#include <iostream>
#include <vector>
#include <cmath>

struct AudioBuffer {
  std::vector<float> samples;
  int sampleRate;
};

AudioBuffer generateTone(float frequency, float duration, int sampleRate = 44100) {
  AudioBuffer buf;
  buf.sampleRate = sampleRate;
  int numSamples = static_cast<int>(duration * sampleRate);
  buf.samples.resize(numSamples);
  for(int i = 0; i < numSamples; i++) {
    buf.samples[i] = std::sin(2.0f * M_PI * frequency * i/sampleRate);
  }
  return buf;
}

int main() {
  auto buf = generateTone(440.0f, 1.0f);
  std::cout << "Sample generated: " << buf.samples.size() << "\n";
  return 0;
}
