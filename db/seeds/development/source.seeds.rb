after "development:category" do
  Source.delete_all

  puts "Creating sources"
  %w(http://www.ruby-lang.org/en/feeds/news.rss).each do |url|
    Source.create(link: url, name: 'Ruby Lang', website: 'http://www.ruby-lang.org')
  end
end
