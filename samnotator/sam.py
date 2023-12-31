from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
import torch


device = 'mps' if torch.backends.mps.is_available() else 'cpu'
print(device)

check_point = 'models/sam_vit_h_4b8939.pth'

sam = sam_model_registry["vit_h"](checkpoint=check_point)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(
                                            model=sam,
                                            points_per_side=2,
                                            pred_iou_thresh=0.9,
                                            stability_score_thresh=0.96,
                                            crop_n_layers=1,
                                            crop_n_points_downscale_factor=2,
                                            min_mask_region_area=100, # Requires open-cv to run post-processing
                                            )

