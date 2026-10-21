#include "Job.h"
#include "Image.h"
#include "Scene.h"


namespace pr {
class PixelJob : public Job {
    const Scene &scene;
    Image &img;
    int x, y;

public:
    PixelJob(const Scene &s, Image &i, int px, int py) : scene(s), img(i), x(px), y(py){}

    void run() override{
        const Scene::screen_t &screen = scene.getScreenPoints();
        auto &screenPoint = screen[y][x];
        Ray ray(scene.getCameraPos(), screenPoint);
        int targetSphere = scene.findClosestInter(ray);

        if(targetSphere != -1){
            const Sphere &obj =  scene.getObject(targetSphere);
            Color finalcolor = scene.computeColor(obj, ray);
            img.pixel(x, y) = finalcolor;
        }
    }

};

class LineJob : public Job{
    const Scene &scene;
    Image &img;
    int y;

public:
    LineJob(const Scene &s, Image &i, int py) : scene(s), img(i), y(py){}

    void run() override {
        const Scene::screen_t &screen = scene.getScreenPoints();
        for (int x = 0; x < scene.getWidth(); ++x){
            auto &screenPoint = screen[y][x];
            Ray ray(scene.getCameraPos(), screenPoint);
            int targetSphere = scene.findClosestInter(ray);

            if(targetSphere != -1){
                const Sphere &obj =  scene.getObject(targetSphere);
                Color finalcolor = scene.computeColor(obj, ray);
                img.pixel(x, y) = finalcolor;
            }
        }

    }
};

} // namespace pr
