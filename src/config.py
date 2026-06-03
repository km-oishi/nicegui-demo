body_name_list = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "Left_Wrist",
    "Left_Thumb_CMC",
    "Left_Thumb_MCP",
    "Left_Thumb_IP",
    "Left_Thumb_TIP",
    "Left_Index_Finger_MCP",
    "Left_Index_Finger_PIP",
    "Left_Index_Finger_DIP",
    "Left_Index_Finger_TIP",
    "Left_Middle_Finger_MCP",
    "Left_Middle_Finger_PIP",
    "Left_Middle_Finger_DIP",
    "Left_Middle_Finger_TIP",
    "Left_Ring_Finger_MCP",
    "Left_Ring_Finger_PIP",
    "Left_Ring_Finger_DIP",
    "Left_Ring_Finger_TIP",
    "Left_Pinky_MCP",
    "Left_Pinky_PIP",
    "Left_Pinky_DIP",
    "Left_Pinky_TIP",
    "Right_Wrist",
    "Right_Thumb_CMC",
    "Right_Thumb_MCP",
    "Right_Thumb_IP",
    "Right_Thumb_TIP",
    "Right_Index_Finger_MCP",
    "Right_Index_Finger_PIP",
    "Right_Index_Finger_DIP",
    "Right_Index_Finger_TIP",
    "Right_Middle_Finger_MCP",
    "Right_Middle_Finger_PIP",
    "Right_Middle_Finger_DIP",
    "Right_Middle_Finger_TIP",
    "Right_Ring_Finger_MCP",
    "Right_Ring_Finger_PIP",
    "Right_Ring_Finger_DIP",
    "Right_Ring_Finger_TIP",
    "Right_Pinky_MCP",
    "Right_Pinky_PIP",
    "Right_Pinky_DIP",
    "Right_Pinky_TIP",
]

# 関節間の接続定義 (インデックスは body_name_list に対応)
BODY_CONNECTIONS: list[tuple[int, int]] = [
    (0, 1), (0, 2), (1, 3), (2, 4),       # 顔
    (5, 6),                                 # 肩
    (5, 7), (7, 9),                         # 左腕
    (6, 8), (8, 10),                        # 右腕
    (5, 11), (6, 12), (11, 12),             # 体幹
    (11, 13), (13, 15),                     # 左脚
    (12, 14), (14, 16),                     # 右脚
]

LEFT_HAND_CONNECTIONS: list[tuple[int, int]] = [
    (9, 17),
    (17, 18), (18, 19), (19, 20), (20, 21),   # 親指
    (17, 22), (22, 23), (23, 24), (24, 25),   # 人差し指
    (17, 26), (26, 27), (27, 28), (28, 29),   # 中指
    (17, 30), (30, 31), (31, 32), (32, 33),   # 薬指
    (17, 34), (34, 35), (35, 36), (36, 37),   # 小指
]

RIGHT_HAND_CONNECTIONS: list[tuple[int, int]] = [
    (10, 38),
    (38, 39), (39, 40), (40, 41), (41, 42),   # 親指
    (38, 43), (43, 44), (44, 45), (45, 46),   # 人差し指
    (38, 47), (47, 48), (48, 49), (49, 50),   # 中指
    (38, 51), (51, 52), (52, 53), (53, 54),   # 薬指
    (38, 55), (55, 56), (56, 57), (57, 58),   # 小指
]

ALL_CONNECTIONS: list[tuple[int, int]] = (
    BODY_CONNECTIONS + LEFT_HAND_CONNECTIONS + RIGHT_HAND_CONNECTIONS
)
