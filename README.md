# honeyComb

### Architectural design
#### Usage data flow
![](./architectural_design_use_flow.png)

#### Training flow
![](./architectural_design_training_flow.png)


### Staring the project
```
cd honeycomb
docker compose up
```

### Port mapping
- localhost:12021 -> ingress
- localshot:12022 -> minio


### Ingress mapping
- localhost:12021/api -> center api
- localhost:12021/cls/api -> classification api
- localhost:12021/seg/api -> segmentation api
- localhost:12021/trans/api -> transformation api