def compare_images(prev_image, current_image, noise_threshold=4, contour_area_threshold=50):
    """
    Compare two images and return the change metrics.
    
    Args:
        prev_image: Previous image array
        current_image: Current image array
        noise_threshold: Threshold for noise filtering (default: 4)
        contour_area_threshold: Minimum area for significant contours (default: 50)
    
    Returns:
        tuple: (change_percentage, number of significant contours, list of significant contours)
    """
    # Convert to grayscale
    prev_gray = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
    
    # Compute absolute difference
    diff = cv2.absdiff(prev_gray, curr_gray)
    
    # Apply noise filter using configured threshold
    noise_mask = diff <= noise_threshold
    filtered_diff = diff.copy()
    filtered_diff[noise_mask] = 0
    
    # Find contours on the filtered difference image
    contours, _ = cv2.findContours(filtered_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by configured area threshold
    significant_contours = [c for c in contours if cv2.contourArea(c) > contour_area_threshold]
    total_change_area = sum(cv2.contourArea(c) for c in significant_contours)
    
    # Calculate the change percentage
    total_pixels = curr_gray.shape[0] * curr_gray.shape[1]
    change_percentage = (total_change_area / total_pixels) * 100
    
    return change_percentage, len(significant_contours), significant_contours
