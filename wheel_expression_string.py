ln1 = "global vector $vPos = << 0, 0, 0 >>;\n"
ln2 = "float $distance = 0.0;\n"
ln3 = "int $direction = 1;\n"
ln4 = "vector $vPosChange = `getAttr base_TopGrp.translate`;\n"
ln5 = "float $cx = $vPosChange.x - $vPos.x;\n"
ln6 = "float $cy = $vPosChange.y - $vPos.y;\n"
ln7 = "float $cz = $vPosChange.z - $vPos.z;\n"
ln8 = "float $distance = sqrt( `pow $cx 2` + `pow $cy 2` + `pow $cz 2` );\n"
ln9 = "if ( ( $vPosChange.x == $vPos.x ) && ( $vPosChange.y != $vPos.y ) && ( $vPosChange.z == $vPos.z ) ){}\n"
ln10 = "else {\n"
ln11 = "    float $angle = base_TopGrp.rotateY%360;\n"
ln12 = "    if ( $angle == 0 ){ \n"
ln13 = "        if ( $vPosChange.z > $vPos.z ) $direction = 1;\n"
ln14 = "        else $direction=-1;}\n"
ln15 = "    if ( ( $angle > 0 && $angle <= 90 ) || ( $angle <- 180 && $angle >= -270 ) ){ \n"
ln16 = "        if ( $vPosChange.x > $vPos.x ) $direction = 1 * $direction;\n"
ln17 = "        else $direction = -1 * $direction; }\n"
ln18 = "    if ( ( $angle > 90 && $angle <= 180 ) || ( $angle < -90 && $angle >= -180 ) ){\n"
ln19 = "        if ( $vPosChange.z > $vPos.z ) $direction = -1 * $direction;\n"
ln20 = "        else $direction = 1 * $direction; }\n"
ln21 = "    if ( ( $angle > 180 && $angle <= 270 ) || ( $angle < 0 && $angle >= -90 ) ){\n"
ln22 = "        if ( $vPosChange.x > $vPos.x ) $direction = -1 * $direction;\n"
ln23 = "        else $direction = 1 * $direction; }\n"
ln24 = "    if ( ( $angle > 270 && $angle <= 360 ) || ( $angle < -270 && $angle >= -360 ) ) {\n"
ln25 = "        if ( $vPosChange.z > $vPos.z ) $direction = 1 * $direction;\n"
ln26 = "        else $direction = -1 * $direction; }\n"
ln27 = "    base_TopGrp.Drive = base_TopGrp.Drive + ( ( $direction * ( ( $distance / ( 6.283185 * base_TopGrp.Radius ) ) * 360.0 ) ) ); }\n"
ln28 = "$vPos = << base_TopGrp.translateX, base_TopGrp.translateY, base_TopGrp.translateZ >>;\n"

exp = ln1 + ln2 + ln3 + ln4 + ln5 + ln6 + ln7 + ln8 + ln9 + ln10 + ln11 + ln12 + ln13 + ln14 + ln15 + ln16 + ln17 + ln18 + ln19 + ln20 + ln21 + ln22 + ln23 + ln24 + ln25 + ln26 + ln27 + ln28
