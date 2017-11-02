class RenameCategories < ActiveRecord::Migration[5.0]
  def up
    translate(from: :en, to: :ar)
  end

  def down
    translate(from: :ar, to: :en)
  end

  private

  def translate(from:, to:)
    categories_translations.each do |translations|
      Category
        .where(name: translations[from])
        .update_all(name: translations[to])
    end
  end

  def categories_translations
    [
      { en: "Breaking", ar: "عاجل" },
      { en: "Local", ar: "محلي" },
      { en: "Regional", ar: "عربي" },
      { en: "International", ar: "دولي" },
      { en: "Economy", ar: "اقتصاد" },
      { en: "Society", ar: "مجتمع" },
      { en: "Health", ar: "صحة" },
      { en: "Sports", ar: "رياضة" },
      { en: "Reports", ar: "تقارير" },
      { en: "Entertainment", ar: "أخبار" },
      { en: "Opinion", ar: "آراء" },
      { en: "General", ar: "عام" }
    ]
  end
end
