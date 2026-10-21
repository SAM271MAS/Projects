#ifndef TASKS_H
#define TASKS_H

#include <QImage>
#include <filesystem>
#include "BoundedBlockingQueue.h"

namespace pr {

using FileQueue = BoundedBlockingQueue<std::filesystem::path>;

const std::filesystem::path FILE_POISON{};

// load/resize/save 
void treatImage(FileQueue& fileQueue, const std::filesystem::path& outputFolder);


struct TaskData {
    QImage image;

    std::filesystem::path filename;


    TaskData(QImage img = QImage(), std::filesystem::path name = ""): image(std::move(img)), filename(std::move(name)) {}

    size_t byteCount() const {
        return image.sizeInBytes();
    }

    bool isPoison() const {
        return image.isNull() && filename.empty();
    }

};

const TaskData TASK_POISON{};

//using ImageTaskQueue = BoundedBlockingQueue<TaskData*>;
// or
using ImageTaskQueue = BoundedBlockingQueue<TaskData>;

void reader(FileQueue& fileQueue, ImageTaskQueue& imageQueue);
void resizer(ImageTaskQueue& imageQueue, ImageTaskQueue& resizedQueue);
void saver(ImageTaskQueue& resizedQueue, const std::filesystem::path& outputFolder);

} // namespace pr

#endif // TASKS_H
