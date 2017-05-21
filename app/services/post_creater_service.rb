class PostCreaterService
  IMG_TAG_REGEXP = %r{<img[^>]+\/>}
  URL_REGEXP = /(?<=src=(\"|\'))[^\"\']+/

  def add_post(item, source)
    post = Post.new(post_params(item, source))
    post.state = :approved if source.whitelisted
    post.categories = [source.category] if source.category.present?
    source.update(state: Source.state.not_full_info) unless post.save
  end

  def post_params(item, source)
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
    service = KeywordsService.new(description: description)
    { keywords: service.keywords, posts: service.dependent_post }
  end
end
