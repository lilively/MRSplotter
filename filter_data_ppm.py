def get_PPM(ppm, NPoint, MaxPPM, MinPPM):
        """
        Convert the given ppm to the corresponding point index.
        :param ppm: The given PPM value.
        :param NPoint: The total number of data points.
        :param MaxPPM: The maximum PPM value of the range.
        :param MinPPM: The minimum PPM value of the range.
        :return: The corresponding index (point).
        """

        if not (MinPPM <= ppm <= MaxPPM):
            raise ValueError(f"PPM {ppm} is out of range ({MinPPM}, {MaxPPM}).")
        
        delta = abs(MaxPPM - MinPPM) / (NPoint)
        point = round((MaxPPM - ppm) / delta)
        # point = max(0, min(point, NPoint - 1))
        return point
