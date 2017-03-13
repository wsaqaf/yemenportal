after "development:category", "development:source" do
  Post.delete_all

  puts "Creating new posts"
  30.times do
    post = Post.create(description: Faker::StarWars.quote, title: Faker::StarWars.character, link: Faker::Internet.url,
      published_at: Faker::Time.between(12.days.ago, Date.today, :all),
      source: Source.order("RANDOM()").first)
    PostCategory.create(post: post, category: Category.order("RANDOM()").first)
  end
end
