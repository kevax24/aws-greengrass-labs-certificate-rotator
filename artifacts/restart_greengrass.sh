sudo systemctl stop greengrass.service
sudo cp /greengrass/v2/work/com.doka.CertificateRotator/effectiveConfig.yaml /root/effectiveConfig.yaml.bak
sudo cp /greengrass/v2/work/com.doka.CertificateRotator/thingCert.crt /root/thingCert.crt.bak
sudo cp /greengrass/v2/work/com.doka.CertificateRotator/effectiveConfig.yaml /greengrass/v2/config/effectiveConfig.yaml
sudo cp /greengrass/v2/work/com.doka.CertificateRotator/thingCert.crt /greengrass/v2/thingCert.crt
sudo java -Droot="/greengrass/v2" \
    -jar /greengrass/v2/alts/current/distro/lib/Greengrass.jar \
    --start false \
    --init-config /greengrass/v2/config/effectiveConfig.yaml
sudo systemctl start greengrass.service

systemctl disable restart_gg.service