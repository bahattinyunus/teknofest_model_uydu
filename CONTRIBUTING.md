# Katkı Rehberi – TEKNOFEST Model Uydu

Projeye katkıda bulunmak istediğiniz için teşekkürler! Bu rehber, katkı sürecini kolaylaştırmak için hazırlanmıştır.

## Başlamadan Önce

1. Bir **Issue** açın ve yapmak istediğiniz değişikliği açıklayın.
2. İssue üzerinde mutabık kalındıktan sonra fork yapın ve branch açın.

## Branch Adlandırma

```
feature/yeni-özellik-adı
fix/hata-kısa-açıklaması
docs/güncelleme-konusu
```

## Commit Mesajı Stili

[Conventional Commits](https://www.conventionalcommits.org/) stilini kullanın:

```
feat: yeni PID auto-tuning modülü eklendi
fix: EKF kovaryans matris sıfırlanma hatası düzeltildi
docs: teknik rapor kablolama bölümü güncellendi
test: FSM geçiş testleri kapsam genişletildi
```

## Kod Kalitesi

- PEP 8 uyumlu Python kodu yazın
- Yeni fonksiyonlar için docstring ekleyin
- Değişiklikleriniz için `tests/` dizinine test ekleyin
- `pytest tests/ -v` komutunun hatasız çalıştığından emin olun

## Pull Request Süreci

1. Değişikliklerinizi içeren PR açın
2. PR açıklamasına "Closes #<issue_no>" yazın
3. En az 1 ekip üyesinin incelemesini bekleyin
4. Tüm testler yeşil olduktan sonra merge yapılır

## İletişim

Sorunuz varsa GitHub Issues üzerinden bildirin.
