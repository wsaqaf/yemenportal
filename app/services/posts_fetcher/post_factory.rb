class PostsFetcher::PostFactory
  def initialize(source:, item:)
    @source = source
    @item = item
  end

  def create
    Post.create(post_params)
  end

  private

  attr_reader :source, :item

  delegate :title, :link, :description, :published_at, :image_url, to: :item

  def post_params
    {
      title: title,
      link: link,
      description: description,
      published_at: published_at,
      image_url: image_url,
      source: source
    }
  end
end
