import torch
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2


def clamp(min_val, max_val, value):
    return max(min(max_val, value), min_val)

def boxes_to_groups(boxes):
    groups = []

    for bi, box in enumerate(boxes):
        added_to_group = False

        for gi, group in enumerate(groups):
            for group_box in group:
                y1 = clamp(box[1], box[3], group_box[1])
                y2 = clamp(box[1], box[3], group_box[3])
                y_overlap = (y2 - y1) / (box[3] - box[1])

                if y_overlap >= 0.6:
                    group.append(box)
                    added_to_group = True
                    break

            if added_to_group:
                break

        if not added_to_group:
            groups.append([box])

    for group in groups:
        group.sort(key=lambda box: box[0])
    groups.sort(key=lambda group: group[0][1])

    return groups



def combining_boxes(groups):

    for gi, group in enumerate(groups):
        i = 0

        while i < len(group) - 1:
            box_cur, box_next = group[i], group[i+1]

            x1 = clamp(box_next[0], box_next[2], box_cur[0])
            x2 = clamp(box_next[0], box_next[2], box_cur[2])
            x_overlap = (x2 - x1) / (box_next[2] - box_next[0])

            if x_overlap > 0:
                new_box = torch.stack([
                    torch.min(box_cur[0], box_next[0]), #xmin
                    torch.min(box_cur[1], box_next[1]), #ymin
                    torch.max(box_cur[2], box_next[2]), #xmax
                    torch.max(box_cur[3], box_next[3]), #ymax
                ])

                group[i] = new_box

                del group[i + 1]
                i = max(i - 1, 0)
            else:
                i += 1

    return groups

def show_groups(image, groups):
    temp = image.copy()
    groups = combining_boxes(groups)

    for group in groups:
        color = np.random.randint(256, size=3).tolist()

        for box in group:
            x1, y1, x2, y2 = map(int, box)
            temp = cv2.rectangle(temp, (x1, y1), (x2, y2), color=color, thickness=3)

    plt.figure(figsize=(15, 10))
    plt.imshow(temp)
    plt.axis('off')
    plt.show()

def show_errors(image, groups) -> np.ndarray:
    groups = combining_boxes(groups)

    for group in groups:
        color = np.random.randint(256, size=3).tolist()

        for box in group:
            x1, y1, x2, y2 = map(int, box)
            image = cv2.rectangle(image, (x1, y1), (x2, y2), color=color, thickness=3)

    return image