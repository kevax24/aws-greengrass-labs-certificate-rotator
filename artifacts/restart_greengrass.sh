systemctl stop greengrass.service
mv /greengrass/v2/work/com.doka.CertificateRotator/effectiveConfig.yaml /greengrass/v2/config/effectiveConfig.yaml
mv /greengrass/v2/work/com.doka.CertificateRotator/thingCert.crt /greengrass/v2/thingCert.crt
sudo java -Droot="/greengrass/v2" \
    -jar /greengrass/v2/alts/current/distro/lib/Greengrass.jar \
    --start false \
    --init-config /greengrass/v2/config/effectiveConfig.yaml
systemctl start greengrass.service

systemctl disable restart_gg.service