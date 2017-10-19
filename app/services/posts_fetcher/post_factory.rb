class PostsFetcher::PostFactory
  def initialize(source, item)
    @source = source
    @item = item
  end

  def create
    Post.create(post_params)
  end

  private

  attr_reader :source, :item

  def post_params
    {
      title: item.title,
      link: item.link,
      description: item.description,
      published_at: item.published_at,
      image_url: item.image_url,
      source: source
    }
  end
end
