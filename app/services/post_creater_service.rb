class PostCreaterService
  IMG_TAG_REGEXP = %r{<img[^>]+\/>}
  URL_REGEXP = /(?<=src=(\"|\'))[^\"\']+/
  attr_accessor :added_posts
  attr_reader :source

  def initialize(source)
    @added_posts = []
    @source = source
  end

  def add_post(item)
    post = Post.new(post_params(item))
    post.state = :approved if source.whitelisted
    post.categories = [source.category] if source.category.present?
    if post.save
      @added_posts << post
    else
      source.update(state: Source.state.not_full_info)
    end
  end

  private

  def post_params(item)
    if source.source_type.rss?
      photo_tag = item.description.slice!(IMG_TAG_REGEXP)
      photo_url = photo_tag.present? ? photo_tag.slice(URL_REGEXP) : nil
      { description: item.description, link: item.link, published_at: item.pubDate, source: source,
        title: item.title, photo_url: photo_url }.merge(additional_fields(item.description))
    elsif source.source_type.facebook?
      message = item["message"] || item["name"]
      { description: message, link: item["link"], published_at: item["created_time"], source: source,
      title: message.match(/[^\n\.]+/).to_s, photo_url: item["picture"] }.merge(additional_fields(message))
    end
  end

  def additional_fields(description = "")
    service = TfIdfService.new(description: description)
    { topic: service.post_topic }
  end
end
