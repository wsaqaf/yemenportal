class PostTagForm < Reform::Form
  property :name
  property :description
  property :post
  property :user

  validates :post, :user, :name, presence: true
  validate do
    errors.add(:base, I18n.t("tag.error.invalide_name")) unless tag_list.include?(name)
  end

  def tag_list
    Tag.all.map(&:name) - post.post_tags.map(&:name) + [PostTag::RESOLVE_TAG]
  end
end
