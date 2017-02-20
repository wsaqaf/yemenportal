after "staging:category" do
  Post.delete_all

  puts "Creating new posts"
  3.times do |i|
    post = Post.create(description: 'In #{i} country, was #{i} situation', title: "News #{i}", link: Faker::Internet.url,
      pub_date: Faker::Time.between(12.days.ago, Date.today, :all))
    PostCategory.create(post: post, category: Category.order("RANDOM()").first)
  end
end
