puts "Seeding production"

%w(breaking local regional international economy society health sports reports
entertainment opinion general).each do |name|
  Category.create(name: I18n.t("category.base_list.#{name}"))
end
