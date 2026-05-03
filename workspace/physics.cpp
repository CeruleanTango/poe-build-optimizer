#include <iostream>
#include <vector>
#include <cmath>

struct Vec3 {float x, y, z;};

Vec3 add(Vec3 a, Vec3 b) {
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}
Vec3 scale(Vec3 v, float s) {
    return {v.x * s, v.y * s, v.z * s};
}
float length(Vec3 v) {
    return std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

struct RigidBody {
    Vec3 position, velocity;
    float mass;
};

void simulate(std::vector<RigidBody>& bodies, float dt) {
    Vec3 gravity = {0, -9.8f, 0};
    for(auto& b : bodies) {
        b.velocity = add(b.velocity, scale(gravity, dt));
        b.position = add(b.position, scale(b.velocity, dt));
    }
}

int maint() {
  std::vector<RigidBody> bodies = {{{0,10,0},{0, 0, 0}, 1.0f}};
  for (int i = 0; i < 100; i++) {
    simulate(bodies, 0.016f);
  }
  std::cout << "Final y: " << bodies[0].position.y << "/n";
  return 0;
}
// Adding mid build change
