#include <iostream>
#include <vector>
#include <string>

struct Rect {
  float x, y;
  float width, height;
};

bool contains(const Rect& r, float px, float py) {
  return px >= r.x && px <= r.x + r.width && py >= r.y && py < r.y + r.height;
}

struct UIElement {
  std::string label;
  Rect bounds;
  bool visible;
  virtual void draw() {
    if (visible) std::cout << "Drawing: " << label << "\n";
  }
};

struct Button : UIElement {
  bool onClick(float mx, float my) {
    if (contains(bounds, mx, my)) {
      std::cout << label << "clicked\n";
      return true;
    }
    return false;
  }
};

int main() {
  Button btn;
  btn.label = "Attack";
  btn.bounds = {10, 10, 100, 40};
  btn.visible = true;
  btn.draw();
  btn.onClick(50, 25);
  return 0;
}
 //Commenting to dirty file on zfs
