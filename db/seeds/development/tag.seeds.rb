%w(misleading_title missing_picture irrelevant_picture plagiarised_copied
wrong_category inappropriate_content propaganda_advertising missing_name).each do |name|
  Tag.create(name: I18n.t("tag.base_list.#{name}"))
end
