after "development:category" do
  puts "Creating new posts"
  30.times do
    post = Post.create(description: Faker::StarWars.quote, title: Faker::StarWars.character, link: Faker::Internet.url,
      pub_date: Faker::Time.between(12.days.ago, Date.today, :all))
    PostCategory.create(post: post, category: Category.order("RANDOM()").first)
  end
end
